from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet

from .pagination import Pagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    UserSerializer,
    IngridientSerializer,
    RecipeSerializer,
    TagSerializer
)
from recipes.models import (
    Ingridient,
    Recipe,
    Tag
)
from users.models import User


class IngridientViewSet(ModelViewSet):
    serializer_class = IngridientSerializer
    permission_class = (AllowAny)
    ordering = ('name')
    pagination_class = None
    queryset = Ingridient.objects.all()


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    permission_class = (IsAuthorOrReadOnly)
    ordering = ('id')
    pagination_class = Pagination
    queryset = Recipe.objects.all()


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    permission_class = (AllowAny)
    pagination_class = None
    queryset = Tag.objects.all()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_class = (AllowAny)
    ordering = ('id')
    pagination_class = Pagination
    queryset = User.objects.all()
