from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count

from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            Favourite,
                            RecipeIngredient,
                            ShoppingCart,
                            Subscription)
User = get_user_model()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    list_display_links = ('id', 'user')
    search_fields = ('user__username', 'author__username')
    list_per_page = 25


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites_count', 'cooking_time')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    readonly_fields = ('favorites_count',)
    list_per_page = 25

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(favorites_count=Count('favourite'))

    @admin.display(description='В избранном', ordering='favorites_count')
    def favorites_count(self, obj):
        return obj.favorites_count


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    list_per_page = 25


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 25


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_display_links = ('id', 'user')
    search_fields = ('user__username', 'recipe__name')
    list_per_page = 25


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_display_links = ('id', 'recipe')
    search_fields = ('recipe__name', 'ingredient__name')
    list_per_page = 25


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipes')
    list_display_links = ('id', 'user')
    search_fields = ('user__username', 'recipes__name')
    list_per_page = 25
