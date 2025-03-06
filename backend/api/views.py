from rest_framework import status, mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from djoser.views import UserViewSet
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from .pagination import Pagination, IngredientResultsPagination
from rest_framework.pagination import PageNumberPagination
from .permissions import IsAuthorOrReadOnly, IsUnauthorizedUser
from .serializers import (
    UserSerializer,
    IngridientSerializer,
    IngridientCreateSerializer,
    RecipeSerializer,
    TagSerializer,
    AvatarSerializer
)
from recipes.models import (
    Ingridient,
    Recipe,
    Tag
)
User = get_user_model()

class IngridientViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingridient.objects.all()
    search_fields = ['name']
    http_method_names = ['get']
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']

    def get_serializer_class(self):
        if self.action in ['create']:
            return IngridientCreateSerializer
        return IngridientSerializer


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly, IsUnauthorizedUser)
    ordering = ('id',)
    pagination_class = Pagination
    queryset = Recipe.objects.all()


class TagViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    serializer_class = TagSerializer
    permission_class = (AllowAny)
    pagination_class = None
    queryset = Tag.objects.all()

    @action(detail=False, url_path='me')
    def anonymous_tags(self, request):
        if request.user.is_anonymous:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)


class UserViewSet(UserViewSet):
    serializer_class = UserSerializer
    ordering = ('id')
    pagination_class = Pagination
    queryset = User.objects.all()


    def paginate(self, request):
        paginator = self.pagination_class
        page = paginator.paginate_queryset(queryset, request)
        serializer = UserSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(methods=['GET'],
            detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    
    @action(
        methods=['PUT', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated, IsAuthorOrReadOnly],
        url_path='me/avatar',
    )
    def avatar_put_delete(self, request, *args, **kwargs):
        if self.request.method == 'PUT':
            serializer = AvatarSerializer(
                instance=request.user,
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif self.request.method == 'DELETE':
            user = self.request.user
            user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, url_path='me')
    def anonymous_me(self, request):
        if request.user.is_anonymous:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)
