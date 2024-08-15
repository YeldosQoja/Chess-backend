from django.contrib.auth import authenticate, login
from rest_framework import status, generics
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer, FriendRequestSerialier, GameSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, Friendship, FriendRequest, Game, GameRequest, UserChannel
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q


# Create your views here.
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def user_signin(request):
    try:
        email = request.data["email"]
        password = request.data["password"]
        user = authenticate(email=email, password=password)
        # Attach authenticated user to the current session
        # Essential for authenticating websocket connections
        login(request, user)
        if not user:
            raise AuthenticationFailed(
                "No active account found with the given credentials"
            )
        serializer = UserSerializer(user)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
    except (KeyError, AuthenticationFailed) as error:
        match error:
            case KeyError():
                return Response(
                    {"error": {"message": "Username or(and) password not provided!"}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            case AuthenticationFailed():
                return Response(
                    {"error": {"message": error.detail}},
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def home(request):
    games = Game.objects.filter(is_active=False).order_by("finished_at")
    response_data = {"games": games}
    if games.exists():
        latest_game = games[0]
        response_data["latest_game"] = latest_game
    return Response(response_data, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.exclude(pk=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        query = request.GET.get("query", "")
        if not query:
            return Response([])
        queryset = self.get_queryset().filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user


class ProfileFriendListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.friends


class FriendRequestListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerialier

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(receiver=user, is_active=True)


class ProfileGameListView(generics.ListAPIView):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.profile.games()


class FriendListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        pk = kwargs["pk"]
        user = get_object_or_404(queryset, pk=pk)
        serializer = self.get_serializer(user.friends, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def user_games(request, pk):
    user = get_object_or_404(User, pk=pk)
    games = user.profile.games()
    serializer = GameSerializer(
        games, many=True, context={"request": request, "user": user}
    )
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_friend(request, pk):
    user = request.user
    friend = get_object_or_404(User, pk=pk)
    try:
        if friend in user.friends.all():
            return Response(
                {"message": f"You and {friend} are already friends."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        friend_request = FriendRequest.objects.filter(sender=user, receiver=friend)
        if friend_request.exists():
            return Response(
                {"message": "You have already sent friend request to this user."},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        FriendRequest.objects.create(sender=user, receiver=friend)
        return Response(
            {
                "message": f"You have sent a friend request to the user {friend}",
            },
            status=status.HTTP_201_CREATED,
        )
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_friend(request, pk):
    friend_request = get_object_or_404(FriendRequest, pk=pk)
    friend_request.accept()
    return Response(
        {"message": f"You and {friend_request.sender} have become friends."},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def decline_friend(request, pk):
    friend_request = get_object_or_404(FriendRequest, pk=pk)
    friend_request.decline()
    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_friend(request, pk):
    user = request.user
    friendship = get_object_or_404(Friendship, user=user, friend=pk)
    friendship.break_friendship()
    return Response({"message": "Friendship is broken!"}, status=status.HTTP_200_OK)


channel_layer = get_channel_layer()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_challenge(request, user_id):
    opponent = get_object_or_404(User, pk=user_id)
    # If friend is currently online send message to friend's channel
    friend_channel = UserChannel.objects.filter(user=opponent)
    if not friend_channel.exists():
        return Response({ "message": f"{opponent} is not currently online" }, status=status.HTTP_404_NOT_FOUND)
    if opponent.profile.is_playing():
        return Response({ "message": f"{opponent} is already playing" }, status=status.HTTP_404_NOT_FOUND)
    game_request = GameRequest.objects.create(sender=request.user, receiver=opponent)
    async_to_sync(channel_layer.send)(
        friend_channel.first().name,
        {"type": "on.challenge", "request_id": game_request.pk},
    )
    return Response(status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_challenge(request, pk):
    game_request = get_object_or_404(GameRequest, pk=pk)
    opponent = game_request.sender
    # If sender of request is no longer online, we return error response
    opponent_socket_channel = get_object_or_404(UserChannel, user=opponent)
    # Invalidate game request
    game_request.is_active = False
    game_request.is_accepted = True
    game_request.save()
    game = Game.objects.create(challenger=opponent, opponent=request.user)
    async_to_sync(channel_layer.send)(
        opponent_socket_channel.name,
        {"type": "on.challenge.accept", "game_id": game.pk},
    )
    return Response({"game_id": game.pk}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def decline_challenge(request, pk):
    game_request = get_object_or_404(GameRequest, pk=pk)
    # Invalidate game request
    game_request.is_active = False
    game_request.save()
    return Response(status=status.HTTP_201_CREATED)


class GameRetrieveView(generics.RetrieveAPIView):
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Game.objects.filter(
            Q(challenger=self.request.user) | Q(opponent=self.request.user),
            is_active=True,
        )
