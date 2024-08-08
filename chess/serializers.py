from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Profile, FriendRequest, Game


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
        if request and hasattr(request, "user"):
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


class GameSerializer(serializers.ModelSerializer):
    challenger = UserSerializer()
    opponent = UserSerializer()
    is_white = serializers.SerializerMethodField()

    def get_is_white(self, obj):
        request = self.context["request"]
        if request and hasattr(request, "user"):
            return obj.challenger == request.user
        return False

    class Meta:
        model = Game
        fields = [
            "id",
            "challenger",
            "opponent",
            "winner",
            "is_white",
            "is_active",
            "created_at",
            "started_at",
            "finished_at",
        ]
        read_only_fields = ["is_white"]
