from django.contrib.auth.admin import UserAdmin

from users.models import Follower


class Admin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'icon')
    ordering = ('id')


class AdminFollower(Follower):
    list_display = ('user', 'following')
    search_fields = ('user', 'following')
