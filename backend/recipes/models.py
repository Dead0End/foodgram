from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

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


class Ingridient(models.Model):
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
    #author = models.ForeignKey(
    #    User,
    #    on_delete=models.CASCADE,
    #    verbose_name=('Автор')
    #)
    tag = models.ManyToManyField(
        Tag,
        verbose_name=('Тег')
    )

    class Meta:
        ordering = ('name',)
        verbose_name = ('Рецепт')


class RecipeItself(models.Model):
    """Класс для объединения рецепта и ингридиентов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    Ingridients = models.ForeignKey(
        Ingridient,
        on_delete=models.CASCADE,
        verbose_name=('Ингридиенты')
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


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='cart_items',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='carts',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_entry',
            )
        ]