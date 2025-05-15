from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.db.models import Count

from users.models import Follower, CustomUser
from recipes.models import Recipe, Ingredient, Tag


class Admin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'avatar')
    ordering = ('id')


class AdminFollower(Follower):
    list_display = ('user', 'following')
    search_fields = ('user', 'following')


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_display_links = ('id', 'username')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    list_per_page = 25


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites_count', 'pub_date')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    readonly_fields = ('favorites_count',)
    list_per_page = 25

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(favorites_count=Count('favourite'))

    def favorites_count(self, obj):
        return obj.favorites_count
    favorites_count.short_description = 'В избранном'
    favorites_count.admin_order_field = 'favorites_count'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    list_per_page = 25


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25