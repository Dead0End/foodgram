from rest_framework import routers
from django.urls import path, include, re_path

from api.views import (
    IngredientViewSet,
    TagViewSet,
    UserViewSet,
    RecipeTestViewSet
)

app_name = 'api'

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeTestViewSet, basename='recipes')
router.register(r'recipes', RecipeTestViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
