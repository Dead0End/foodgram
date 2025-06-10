from rest_framework import routers
from django.urls import path, include

from api.views import (
    IngredientViewSet,
    TagViewSet,
    UserViewSet,
    RecipeViewSet,
    redirect_recipe_short_link
)

app_name = 'api'

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('api/users/', UserViewSet.as_view({'get': 'list'}), name='users'),
    path('recipes/<int:recipe_id>/',
         redirect_recipe_short_link,
         name='recipe-short-link'),
]
