from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .constants import (
    USERNAME_MAX_LENGTH, EMAIL_MAX_LENGTH, NAME_MAX_LENGTH,
    USERNAME_VERBOSE, USERNAME_HELP, EMAIL_VERBOSE, EMAIL_HELP,
    FIRST_NAME_VERBOSE, FIRST_NAME_HELP, LAST_NAME_VERBOSE,
    AVATAR_VERBOSE, AVATAR_HELP, AVATAR_UPLOAD_TO,
    USER_VERBOSE, USER_VERBOSE_PLURAL,
    FOLLOWER_UNIQUE_CONSTRAINT_NAME, FOLLOWER_CHECK_CONSTRAINT_NAME
)


class CustomUser(AbstractUser):
    """Обычный пользователь."""
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        verbose_name=USERNAME_VERBOSE,
        help_text=USERNAME_HELP,
        unique=True,
        validators=[UnicodeUsernameValidator]
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        verbose_name=EMAIL_VERBOSE,
        help_text=EMAIL_HELP,
        unique=True,
    )
    first_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name=FIRST_NAME_VERBOSE,
        help_text=FIRST_NAME_HELP,
    )
    last_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name=LAST_NAME_VERBOSE,
    )
    avatar = models.ImageField(
        verbose_name=AVATAR_VERBOSE,
        help_text=AVATAR_HELP,
        upload_to=AVATAR_UPLOAD_TO,
        null=True,
        blank=True 
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = USER_VERBOSE
        verbose_name_plural = USER_VERBOSE_PLURAL

    def __str__(self):
        return self.username


class Follower(models.Model):
    """Пользователь - подписчик."""
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )
    follow = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follow',
        verbose_name='Подписка'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'follow'),
                name=FOLLOWER_UNIQUE_CONSTRAINT_NAME
            ),
            models.CheckConstraint(
                name=FOLLOWER_CHECK_CONSTRAINT_NAME,
                check=~models.Q(user=models.F('follow')),)]
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.user.username} подписан на {self.follow.username}'
