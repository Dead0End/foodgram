from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from filters import (
    ModelMultipleChoiceFilter,
    BooleanFilter)

from recipes.models import Ingridient, Recipe, Tag

User = get_user_model()


class IngridientFilter(FilterSet):
    name = filters.CharFilter(lookup='startswith')

    class Meta:
        model = Ingridient
        fields = ['name']


class RecipeFilter(FilterSet):
    tag = ModelMultipleChoiceFilter(
        name='tags_slug',
        to_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    favourite = BooleanFilter(method='favourite_filter')
    inside_shopping_cart = BooleanFilter(
        method='filter_is_inside_the_shopping_cart')

    def fav_filter(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(favourites_user=user)
        return queryset

    def filter_is_inside_the_shoping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopping_cart_user=user)
        return queryset
