from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follower, User


@admin.register(User)
class UserAdmin(UserAdmin):
    display_list = (
        'id',
        'email',
        'username',
        'name',
        'surname'
    )
    filter_list = ('email', 'name')


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    display_list = ('user', 'author')
