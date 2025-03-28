# Generated by Django 4.2.16 on 2025-03-28 21:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт, добавленный в корзину'),
        ),
        migrations.AddField(
            model_name='shoppinglist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='пользователь, добавивший рецепт в корзину'),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='shoppingcart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='recipeuser',
            name='cooking_time',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Cooking_time', to='recipes.recipe', verbose_name='Время приготовления'),
        ),
        migrations.AddField(
            model_name='recipeuser',
            name='email',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Email', to=settings.AUTH_USER_MODEL, verbose_name='Email'),
        ),
        migrations.AddField(
            model_name='recipeuser',
            name='first_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='First_name', to=settings.AUTH_USER_MODEL, verbose_name='Имя'),
        ),
        migrations.AddField(
            model_name='recipeuser',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Image', to='recipes.recipe', verbose_name='Фото'),
        ),
        migrations.AddField(
            model_name='recipeuser',
            name='last_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Last_name', to=settings.AUTH_USER_MODEL, verbose_name='Фамилия'),
        ),
        migrations.AddField(
            model_name='recipeuser',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Recipe', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='recipeuser',
            name='password',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Password', to=settings.AUTH_USER_MODEL, verbose_name='Пароль'),
        ),
        migrations.AddField(
            model_name='recipeuser',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Tag', to='recipes.recipe', verbose_name='Тег'),
        ),
        migrations.AddField(
            model_name='recipeuser',
            name='text',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Text', to='recipes.recipe', verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='recipeuser',
            name='username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='User', to=settings.AUTH_USER_MODEL, verbose_name='пользователь'),
        ),
        migrations.AddField(
            model_name='recipeitself',
            name='email',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='User.email+', to=settings.AUTH_USER_MODEL, verbose_name='email пользователя'),
        ),
        migrations.AddField(
            model_name='recipeitself',
            name='first_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='User.first_name+', to=settings.AUTH_USER_MODEL, verbose_name='Имя пользователя'),
        ),
        migrations.AddField(
            model_name='recipeitself',
            name='last_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='User.last_name+', to=settings.AUTH_USER_MODEL, verbose_name='Фамилия пользователя'),
        ),
        migrations.AddField(
            model_name='recipeitself',
            name='measurement_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Ingredient.mu+', to='recipes.ingredient', verbose_name='Единицы измерения'),
        ),
        migrations.AddField(
            model_name='recipeitself',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Recipe.name+', to='recipes.recipe', verbose_name='Имя рецепта'),
        ),
        migrations.AddField(
            model_name='recipeitself',
            name='password',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='User.password+', to=settings.AUTH_USER_MODEL, verbose_name='Пароль'),
        ),
        migrations.AddField(
            model_name='recipeitself',
            name='text',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Recipe.text+', to='recipes.recipe', verbose_name='Текст рецепта'),
        ),
        migrations.AddField(
            model_name='recipeitself',
            name='username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='User.username+', to=settings.AUTH_USER_MODEL, verbose_name='Никнейм пользователя'),
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='recipes.tag', verbose_name='Тег'),
        ),
        migrations.AddField(
            model_name='favourite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.recipe', verbose_name='Рецепт, добавленный в избранное'),
        ),
        migrations.AddField(
            model_name='favourite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='пользователь, добавивший рецепт в избранное'),
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together={('user', 'author')},
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('user', 'recipe'), name='unique_cart_entry'),
        ),
    ]
