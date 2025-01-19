from django.apps import AppConfig


class RecipeConfig(AppConfig):
    auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = 'рецепты'
