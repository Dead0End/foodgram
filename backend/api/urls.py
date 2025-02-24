from rest_framework.authtoken import views
from django.urls import include, path
from rest_framework import routers

from api.views import (
    IngridientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
)

app_name = 'api'

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngridientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),  # токены
    path('', include(router.urls)),
    # path('auth/', include('djoser.urls.jwt')),
]