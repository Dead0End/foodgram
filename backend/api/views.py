from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status

from recipes.models import (Ingridient, Recipe, Tag)
from serializers import (IngredientSerializer, ShortSerializer, TagSerializer)
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .pagination import Pagination
from .filters import IngredientFilter, RecipeFilter


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingridient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = IsAdminOrReadOnly
    filter_backends = (DjangoFilterBackend)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAdminOrReadOnly | IsAuthorOrReadOnly)
    pagignation_class = Pagination
    filter_backends = (DjangoFilterBackend)
    filterset_class = RecipeFilter

    def add_to(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_from(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly)
