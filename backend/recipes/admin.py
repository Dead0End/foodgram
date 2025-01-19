from django.contrib import admin
from django.contrib.admin import ModelAdmin, display

from .models import (Recipe, Ingridient)


@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    display_list = ('name', 'id', 'author')
    filter_list = ('name', 'author', 'tags')

    @display()
    def favourite(self, obj):
        return obj.favourite.count()


@admin.register(Ingridient)
class IngridientAdmin(ModelAdmin):
    display_list = ('name', 'unit_of_measurment')
    filter_list = ('name')
