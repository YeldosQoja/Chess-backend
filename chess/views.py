from django.contrib.auth import authenticate
from rest_framework import status, generics
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer, FriendRequestSerialier
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


# Create your views here.
@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def user_signin(request):
    try:
        email = request.data["email"]
        password = request.data["password"]
        user = authenticate(email=email, password=password)
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


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.exclude(pk=self.request.user.pk)

    def get(self, request, *args, **kwargs):
        username = request.GET.get("username", "")
        queryset = self.get_queryset().filter(username__icontains=username)
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


class FriendListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.friends


class FriendRequestListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerialier

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(receiver=user, is_active=True)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_friend(request):
    user = request.user
    friend_id = request.data["friend"]
    friend = get_object_or_404(User, pk=friend_id)
    try:
        FriendRequest.objects.create(sender=user, receiver=friend)
        return Response(
            {"message": f"You have send a friend request to the user {friend}"},
            status=status.HTTP_201_CREATED,
        )
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_friend(request):
    user = request.user
    friend_id = request.data["friend"]
    friend = get_object_or_404(User, pk=friend_id)
    try:
        friend_request = FriendRequest.objects.get(sender=friend, receiver=user)
        friend_request.accept()
        return Response(
            {"message": f"You and {friend.username} have become friends."},
            status=status.HTTP_201_CREATED,
        )
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def decline_friend(request):
    user = request.user
    friend_id = request.data["friend"]
    friend = get_object_or_404(User, pk=friend_id)
    try:
        friend_request = FriendRequest.objects.get(sender=friend, receiver=user)
        friend_request.decline()
        return Response(status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_friend(request):
    user = request.user
    friend = request.data["friend"]
    friendship = get_object_or_404(Friendship, user=user, friend=friend)
    friendship.break_friendship()
    return Response({"message": "Friendship is broken!"}, status=status.HTTP_200_OK)


channel_layer = get_channel_layer()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_challenge(request):
    user = request.user
    friend_id = request.data["opponent"]
    friend = get_object_or_404(User, pk=friend_id)
    # If they are not friend return response with error
    if friend not in user.friends.all() or user not in friend.friends.all():
        return Response(
            {"error": f"I'm sorry, but {friend.username} is not your friend."},
            status=status.HTTP_404_NOT_FOUND,
        )
    game_request = GameRequest.objects.create(sender=user, receiver=friend)
    # If friend is currently online send message to friend's channel
    friend_socket_channel = UserChannel.objects.filter(user=friend)
    if friend_socket_channel.exists():
        async_to_sync(channel_layer.send)(
            friend_socket_channel.first().name,
            {"type": "on.challenge", "request_id": game_request.pk},
        )
    return Response(status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_challenge(request):
    user = request.user
    game_request_id = request.data["request"]
    game_request = get_object_or_404(GameRequest, pk=game_request_id)
    friend = game_request.sender
    friend_socket_channel = UserChannel.objects.filter(user=friend)
    # If sender of request is no longer online, we return error response
    if not friend_socket_channel.exists():
        return Response(
            {"error": "Your opponent is not online."}, status=status.HTTP_403_FORBIDDEN
        )
    game_request.is_active = False
    game_request.save()
    game = Game.objects.create(challenger=game_request.sender, opponent=user)
    async_to_sync(channel_layer.send)(
        friend_socket_channel.first().name,
        {"type": "on.challenge.accept", "game_id": game.pk},
    )
    return Response(status=status.HTTP_201_CREATED)
