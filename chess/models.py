from django.db import models
from django.db.models import Q
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils import timezone
from django.conf import settings


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        profile = Profile(user=user)
        profile.save(using=self._db)

        return user

    def create_superuser(self, email, username, password, **extra_fields):
        user = self.create_user(
            email=email, username=username, password=password, **extra_fields
        )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_joined = models.DateTimeField(default=timezone.now)
    friends = models.ManyToManyField("self", through="Friendship")
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def is_staff(self):
        return self.is_admin


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    avatar = models.URLField(null=True)

    def is_playing(self):
        return Game.objects.filter(Q(challenger=self.user) | Q(opponent=self.user), is_active=True).exists()

    def games(self):
        return Game.objects.filter(Q(challenger=self.user) | Q(opponent=self.user), is_active=False).order_by("-finished_at")

    def wins(self):
        user_games = self.games()
        return user_games.filter(winner=self.user.pk).count()

    def losses(self):
        user_games = self.games()
        return user_games.exclude(winner=self.user.pk).count()

    def draws(self):
        user_games = self.games()
        return user_games.filter(winner=None).count()


class Friendship(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user"
    )
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="friend"
    )

    def break_friendship(self):
        """
        Breaks a friendship between two users.
        It can happen from both sides, the initiator for breaking friendship could be user or friend as well.
        1. self.delete() to delete friend from the initiator's friend list.
        2. friend.friends.remove(self.user) to delete the initiator from his friend's friend list
        """
        self.delete()
        self.friend.friends.remove(self.user)


class FriendRequest(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver"
    )
    is_accepted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.sender.username} requested to {self.receiver.username}."

    def accept(self):
        """
        When receiver accepts a request.
        """
        if self.is_active is False:
            return
        self.sender.friends.add(self.receiver)
        self.receiver.friends.add(self.sender)
        self.is_active = False
        self.save()

    def decline(self):
        """
        When receiver declines a request.
        """
        self.is_active = False
        self.save()


class Game(models.Model):
    challenger = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="challenger"
    )
    opponent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="opponent"
    )
    winner = models.IntegerField(null=True, default=None)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)

    def finish(self, winner, finished_at):
        self.is_active = False
        self.finished_at = finished_at
        self.winner = winner.pk
        self.save()


class GameRequest(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="game_sender"
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="game_receiver"
    )
    is_accepted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)


class UserChannel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
