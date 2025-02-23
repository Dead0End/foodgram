from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import AnonymousUser


from .pagination import Pagination
from rest_framework.pagination import PageNumberPagination
from .permissions import IsAuthorOrReadOnly, IsUnauthorizedUser
from .serializers import (
    UserSerializer,
    IngridientSerializer,
    RecipeSerializer,
    TagSerializer,
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
    permission_class = (IsAuthorOrReadOnly,
                        IsUnauthorizedUser)
    ordering = ('id')
    pagination_class = Pagination
    queryset = Recipe.objects.all()
    
    def paginate(self, request):
        paginator = self.pagination_class
        page = paginator.paginate_queryset(queryset, request)
        serializer = RecipeSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    permission_class = (AllowAny)
    pagination_class = None
    queryset = Tag.objects.all()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    permission_class = (IsAuthorOrReadOnly, IsUnauthorizedUser)
    ordering = ('id')
    pagination_class = Pagination
    queryset = User.objects.all()


    def paginate(self, request):
        paginator = self.pagination_class
        page = paginator.paginate_queryset(queryset, request)
        serializer = UserSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class UserCreateView(ModelViewSet):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

