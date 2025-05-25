from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model

from .constants import (
    MAX_LENGTH_NAME,
    MAX_LENGTH_SLUG,
    MAX_LENGTH_TEXT,
    MAX_LENGTH_MEASUREMENT,
    MIN_COOKING_TIME,
    SELF_SUBSCRIBE_ERROR
)
User = get_user_model()


class Tag(models.Model):
    """Класс тега."""
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Тег',
        unique=True,
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG,
        verbose_name='Тег',
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'


class Ingredient(models.Model):
    """Класс ингредиента."""
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Ингредиент',
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_MEASUREMENT,
        verbose_name='Единицы измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Класс рецепта."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор'
    )
    name = models.CharField(
        max_length=MAX_LENGTH_NAME,
        verbose_name='Название',
    )
    text = models.CharField(
        max_length=MAX_LENGTH_TEXT,
        verbose_name='Рецепт'
    )
    image = models.ImageField(
        verbose_name='Фото',
        upload_to='recipes/images'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время на приготовление',
        validators=[
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(32767)
        ]
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeItself(models.Model):
    """Класс для объединения рецепта и ингридиентов."""
    name = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='имя ингридиента',
        related_name='Ingredient.name'
    )
    measurement_unit = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Единицы измерения',
        related_name='Ingredient.mu+'
    )
    name = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Имя рецепта',
        related_name='Recipe.name+'
    )
    text = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Текст рецепта',
        related_name='Recipe.text+'
    )
    username = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Никнейм пользователя',
        related_name='User.username+'
    )
    first_name = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Имя пользователя',
        related_name='User.first_name+'
    )
    last_name = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Фамилия пользователя',
        related_name='User.last_name+'
    )
    email = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='email пользователя',
        related_name='User.email+'
    )
    password = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пароль',
        related_name='User.password+'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Рецепт'


class Favourite(models.Model):
    """Класс рецепта, добавленного в избранное"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь, добавивший рецепт в избранное'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт, добавленный в избранное'
    )

    class Meta:
        verbose_name = 'Понравившееся'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь, добавивший рецепт в корзину'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт, добавленный в корзину'
    )

    class Meta:
        verbose_name = 'Корзина'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def clean(self):
        if self.user == self.author:
            raise ValidationError(SELF_SUBSCRIBE_ERROR)

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Ингредиент'
    )
    amount = models.IntegerField(
        verbose_name='Количество'
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='Пользователь',
    )
    recipes = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='название рецепта',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipes'],
                name='unique_shopping_cart'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
