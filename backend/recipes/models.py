from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from models import Model

User = get_user_model()


class Recipe(Model):
    """Рецепт."""
    author = models.Foreign_key(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='author',
        verbose_name='автор'
    )
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/'
    )
    ingredients = models.ManyToManyField(
        related_name='Inggredients',
        verbose_name='ингридиенты'
    )
    tag = models.ManyToManyField(
        related_name='tagg',
        verbose_name='тег'
    )
    time_to_cook = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class Tag(Model):
    """Тег."""
    name = models.CharField(
        unique=True,
        max_length=200
    )
    slug = models.SlugField(
        unique=True,
        max_length=200
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingridient(Model):
    name = models.CharField(max_length=200)
    unit_of_measurment = models.CharField(max_length=200)

    class meta:
        ordering = ['name']
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.unit_of_measurment}'
