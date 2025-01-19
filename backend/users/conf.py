from django.apps import AppConfig


class UserConfig(AppConfig):
    auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'пользователи'
