from rest_framework import routers
from django.urls import path, include

from api.views import (
    IngredientViewSet,
    TagViewSet,
    UserViewSet,
    RecipeViewSet,
    ShortLinkRedirectView
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
    path('api/users/me/', UserViewSet.as_view({'get': 'me'}), name='user-me'),
    path('s/<int:recipe_id>/', ShortLinkRedirectView.as_view(),
         name='short-link')
]
