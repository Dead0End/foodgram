from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser
from .constants import (
    MAX_TAG_NAME_LENGTH, MAX_TAG_SLUG_LENGTH,
    MAX_INGREDIENT_NAME_LENGTH, MAX_MEASUREMENT_UNIT_LENGTH,
    MAX_RECIPE_NAME_LENGTH, MAX_RECIPE_TEXT_LENGTH,
    MIN_COOKING_TIME, RECIPE_IMAGE_UPLOAD_PATH
)

User = get_user_model()


class Tag(models.Model):
    """Класс тега."""
    name = models.CharField(
        max_length=MAX_TAG_NAME_LENGTH,
        verbose_name='Тег',
        unique=True,
        blank=False
    )
    slug = models.SlugField(
        max_length=MAX_TAG_SLUG_LENGTH,
        verbose_name='Тег',
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Класс ингридиента."""
    name = models.CharField(
        max_length=MAX_INGREDIENT_NAME_LENGTH,
        verbose_name='Ингридиенты',
        blank=False
    )
    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMENT_UNIT_LENGTH,
        verbose_name='Единицы измерения',
        blank=False
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'

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
        max_length=MAX_RECIPE_NAME_LENGTH,
        verbose_name='Название',
    )
    text = models.CharField(
        max_length=MAX_RECIPE_TEXT_LENGTH,
        verbose_name='Рецепт'
    )
    image = models.ImageField(
        verbose_name='Фото',
        upload_to=RECIPE_IMAGE_UPLOAD_PATH
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время на приготовление',
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_amounts',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes_used',
        verbose_name='Ингредиент'
    )
    amount = models.IntegerField(
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


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
        verbose_name_plural = 'Понравившееся'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favourite'
            )
        ]

    def __str__(self):
        return f'{self.user} likes {self.recipe}'


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
            raise ValidationError("Вы не можете подписаться на себя")

    def __str__(self):
        return f"{self.user.username} подписан на {self.author.username}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.recipe} в списке покупок у {self.user}'
