from django.contrib.auth.models import AbstractUser as AbsUser
from django.db import models
from django.db.models import UniqueConstraint as UC
from django.db.models import Model


class User(AbsUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'surname'
    ]
    email = models.EmailField(
        max_length=254,
        unique=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Follower(Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='автор'
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            UC(fields=['user', 'author'],
               name='unique_follow')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
