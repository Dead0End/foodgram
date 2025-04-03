from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import (UnicodeUsernameValidator)
from django.db import models


class CustomUser(AbstractUser):
    """Обычный пользователь."""
    username = models.CharField(
        max_length=150,
        verbose_name='имя пользователя',
        help_text='Обязательное поле',
        unique=True,
        validators=[UnicodeUsernameValidator]
    )
    email = models.CharField(
        max_length=150,
        verbose_name='электронная почта',
        help_text='обязательное поле',
        unique=True,
        blank=False,
        null=False,
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='настоящее имя пользователя',
        help_text='обязательное поле',
        blank=False,
        null=False
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия пользователя',
        blank=False,
        null=False
    )
    password = models.CharField(
        max_length=32,
        verbose_name='Пароль',
        blank=False,
        null=False
    )
    avatar = models.ImageField(
        verbose_name='Аватар пользователя',
        help_text='вы можете загрузить отображаемое фото',
        upload_to='users/avatars',
        null=True
    )

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'password']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

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
        related_name='follow')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'user',
                    'follow'),
                name='me0'),
            models.CheckConstraint(
                name='me1',
                check=~models.Q(user=models.F('follow')),
            )]

    def __str__(self):
        return (
            f'{self.user.username} подписан на {self.follow.username}'
        )
