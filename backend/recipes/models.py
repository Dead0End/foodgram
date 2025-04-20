from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth import get_user_model
from users.models import CustomUser

User = get_user_model()


class Tag(models.Model):
    """Класс тега."""
    name = models.CharField(
        max_length=150,
        verbose_name='Тег',
        unique=True,
        blank=False
    )
    slug = models.SlugField(
        max_length=150,
        verbose_name='Тег',
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = ('Тег')


class Ingredient(models.Model):
    """Класс ингридиента."""
    name = models.CharField(
        max_length=150,
        verbose_name='Ингридиенты',
        blank=False
    )
    measurement_unit = models.CharField(
        max_length=150,
        verbose_name=('Единицы измерения'),
        blank=False
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингридиенты'


class Recipe(models.Model):
    """Класс рецепта."""
    name = models.CharField(
        max_length=150,
        verbose_name=('Название'),
    )
    text = models.CharField(
        max_length=800,
        verbose_name=('Рецепт')
    )
    image = models.ImageField(
        verbose_name=('Фото'),
        upload_to=('recipes/images')
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время на приготовление',
        validators=[
            MinValueValidator(1)]
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=('Тег')
    )

    class Meta:
        ordering = ('name',)
        verbose_name = ('Рецепт')


class RecipeUser(models.Model):
    username = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='User',
        verbose_name='пользователь',
        blank=False
    )
    email = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='Email',
        verbose_name='Email',
        blank=False
    )
    password = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='Password',
        verbose_name='Пароль',
        blank=False
    )
    first_name = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='First_name',
        verbose_name='Имя',
        blank=False
    )
    last_name = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='Last_name',
        verbose_name='Фамилия',
        blank=False
    )
    name = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='Recipe',
        verbose_name='Рецепт',
        blank=False
    )
    text = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='Text',
        verbose_name='Текст',
        blank=False

    )
    image = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='Image',
        verbose_name='Фото',
        blank=False
    )
    cooking_time = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='Cooking_time',
        verbose_name='Время приготовления',
        blank=False
    )
    tag = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='Tag',
        verbose_name='Тег',
        blank=False
    )


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
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Никнейм пользователя',
        related_name='User.username+'
    )
    first_name = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Имя пользователя',
        related_name='User.first_name+'
    )
    last_name = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Фамилия пользователя',
        related_name='User.last_name+'
    )
    email = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='email пользователя',
        related_name='User.email+'
    )
    password = models.ForeignKey(
        CustomUser,
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
        verbose_name=('пользователь, добавивший рецепт в избранное')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=('Рецепт, добавленный в избранное')
    )

    class Meta:
        verbose_name = ('Понравившееся')


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=('пользователь, добавивший рецепт в корзину')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=('Рецепт, добавленный в корзину')
    )

    class Meta:
        verbose_name = ('Корзина')


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
    recipe = models.ForeignKey(
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