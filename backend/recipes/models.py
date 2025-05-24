from django.core.validators import MinValueValidator
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
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )

    class Meta:
        ordering = ('name',)
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
    """Связующая модель для ингредиентов в рецепте."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',  # Улучшенный related_name
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                1,
                message='Количество должно быть не менее 1'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
                violation_error_message='Этот ингредиент уже есть в рецепте'
            )
        ]
        ordering = ['ingredient__name']  # Сортировка по названию ингредиента

    def __str__(self):
        return f'{self.ingredient.name} - {self.amount} {self.ingredient.measurement_unit}'

    def clean(self):
        """Дополнительная валидация."""
        if self.amount <= 0:
            raise ValidationError(
                {'amount': 'Количество должно быть положительным числом'}
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
