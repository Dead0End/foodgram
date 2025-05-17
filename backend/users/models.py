from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .constants import (
    USERNAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH,
    FOLLOWER_UNIQUE_CONSTRAINT_NAME,
    FOLLOWER_SELF_FOLLOW_CONSTRAINT_NAME
)


class CustomUser(AbstractUser):
    """Обычный пользователь."""
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH,
        verbose_name='имя пользователя',
        help_text='Обязательное поле. Не более 150 символов.',
        unique=True,
        validators=[UnicodeUsernameValidator],
        blank=True,  # Разрешаем пустое значение, так как будем использовать email
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        verbose_name='электронная почта',
        help_text='Обязательное поле',
        unique=True,
    )
    first_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='имя',
        help_text='Обязательное поле',
    )
    last_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='фамилия',
    )
    avatar = models.ImageField(
        verbose_name='аватар',
        help_text='Вы можете загрузить отображаемое фото',
        upload_to='users/avatars/',
        null=True,
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ['email']

    def __str__(self):
        return self.email


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
        related_name='following',
        verbose_name='автор',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'follow'),
                name=FOLLOWER_UNIQUE_CONSTRAINT_NAME,
            ),
            models.CheckConstraint(
                name=FOLLOWER_SELF_FOLLOW_CONSTRAINT_NAME,
                check=~models.Q(user=models.F('follow')),
            )
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.follow.username}'
