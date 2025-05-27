from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count

from users.models import Follower
from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            Favourite,
                            RecipeIngredient,
                            ShoppingCart,
                            Subscription)
User = get_user_model()


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar'
    )
    list_display_links = ('id', 'username')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    ordering = ('username',)
    list_per_page = 25
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info',
         {'fields': (
             'first_name',
             'last_name',
             'email',
             'avatar')}),
        ('Permissions',
         {'fields': (
             'is_active',
             'is_staff',
             'is_superuser',
             'groups',
             'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'follow')
    list_display_links = ('id', 'user')
    search_fields = ('user__username', 'follow__username')
    list_per_page = 25
