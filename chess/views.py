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
from .models import User, Friendship, FriendRequest
from django.shortcuts import get_object_or_404


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


class ProfileUserRetrieveView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


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
def accept_friend_request(request):
    user = request.user
    friend_id = request.data["friend"]
    friend = get_object_or_404(User, pk=friend_id)
    try:
        friend_request = FriendRequest.objects.get(sender=friend, receiver=user)
        friend_request.accept()
        return Response(status=status.HTTP_201_CREATED)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def decline_friend_request(request):
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
def break_friendship(request):
    user = request.user
    friend = request.data["friend"]
    friendship = get_object_or_404(Friendship, user1=user, user2=friend)
    friendship.break_friendship()
    return Response({"message": "Friendship is broken!"}, status=status.HTTP_200_OK)
