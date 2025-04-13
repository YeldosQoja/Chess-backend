from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Profile, FriendRequest, Game, ChatRoom, ChatMessage, Move


User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["user", "avatar", "wins", "losses", "draws"]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "password",
            "profile",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request", None)
        if request and hasattr(request, "user") and not request.user.is_anonymous:
            representation["is_friend"] = request.user.friends.filter(
                pk=instance.pk
            ).exists()
            representation["is_requested"] = FriendRequest.objects.filter(
                sender=request.user, receiver=instance, is_active=True
            ).exists()
        return representation


class FriendRequestSerialier(serializers.ModelSerializer):
    sender = UserSerializer()

    class Meta:
        model = FriendRequest
        fields = ["id", "sender", "created_at", "is_active", "is_accepted"]
        extra_kwargs = {"is_active": {"read_only": True}}


class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = [
            "player",
            "notation",
            "start_x",
            "start_y",
            "end_x",
            "end_y",
            "created_at",
        ]


class GameSerializer(serializers.ModelSerializer):
    white = UserSerializer()
    black = UserSerializer()
    winner = UserSerializer()
    moves = MoveSerializer(many=True)

    class Meta:
        model = Game
        fields = [
            "id",
            "white",
            "black",
            "winner",
            "is_active",
            "created_at",
            "started_at",
            "finished_at",
            "moves",
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get("request", None)
        if request and hasattr(request, "user"):
            user = self.context.get("user", None)
            if user is None:
                user = request.user

            color = instance.get_color(user)
            ret["color"] = color

        return ret


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "room", "sender", "content", "created_at", "edited_at"]


class ChatRoomSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = ChatRoom
        fields = ["id", "members", "created_at", "updated_at"]
