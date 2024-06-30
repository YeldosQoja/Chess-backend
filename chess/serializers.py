from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import FriendRequest

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class FriendRequestSerialier(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ["id", "sender", "receiver", "created_at", "is_active"]
        extra_kwargs = {"is_active": {"read_only": True}}
