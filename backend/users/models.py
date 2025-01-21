from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .validators import (
    image_validation
)

class User(AbstractUser):
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
        null=False
    )
    name = models.CharField(
        max_length=150,
        verbose_name='настоящее имя пользователя',
        help_text='обязательное поле',
        blank=False,
        null=False
    )
    surname = models.CharField(
        max_length=150,
        verbose_name='Фамилия пользователя',
        blank=False,
        null=False
    )
    icon=models.ImageField(
        verbose_name='Аватар пользователя',
        help_text='вы можете загрузить отображаемое фото',
        upload_to='users/',
        validators=[image_validation]
    )

    REQUIRED_FIELDS = ['username', 'name', 'surname', 'email']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username
    

class Follower(models.Model):
    """Пользователь - подписчик."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )
    follow = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follow')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = (
                    'user',
                    'following'
                    )),
            models.CheckConstraint(
                check=~models.Q(user=models.F('follower')),
            )]

    def __str__(self):
        return (
            f'{self.user.username} подписан на {self.follow.username}'
        )