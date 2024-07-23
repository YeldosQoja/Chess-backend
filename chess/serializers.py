from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Profile, FriendRequest, Game


User = get_user_model()


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["id", "challenger", "opponent", "winner", "is_active", "created_at", "started_at", "finished_at"]


class ProfileSerializer(serializers.ModelSerializer):
    games = GameSerializer(many=True)
    class Meta:
        model = Profile
        fields = ["user", "avatar", "games", "wins", "losses", "draws"]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "date_joined", "password", "profile"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class FriendRequestSerialier(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ["id", "sender", "receiver", "created_at", "is_active"]
        extra_kwargs = {"is_active": {"read_only": True}}
