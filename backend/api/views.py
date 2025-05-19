from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.conf import settings
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse

from .pagination import Pagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    UserSerializer,
    IngridientSerializer,
    TagSerializer,
    AvatarSerializer,
    SubscriptionSerializer,
    RecipeTestSerializer,
    RecipeShortSerializer
)
from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    Subscription,
    ShoppingCart,
    Favourite
)
from api.filters import IngredientFilter

User = get_user_model()


class IngridientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    search_fields = ['name']
    http_method_names = ['get']
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    filterset_fields = ['name']

    def get_serializer_class(self):
        return IngridientSerializer


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    permission_class = (AllowAny)
    pagination_class = None
    queryset = Tag.objects.all()


class UserViewSet(UserViewSet):
    serializer_class = UserSerializer
    ordering = ('id')
    queryset = User.objects.all()
    pagination_class = Pagination

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
            return Response({'detail': 'Unauthorized'},
                            status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, pk=self.kwargs['id'])
        if request.method == "POST":
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST)

            if Subscription.objects.filter(
                    user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                subscription = Subscription.objects.create(
                    user=user, author=author)
                serializer = SubscriptionSerializer(subscription)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"Ошибка при создании подписки: {e}")
                return Response(
                    {'errors': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            author = get_object_or_404(User, pk=self.kwargs['id'])
            subscription = Subscription.objects.filter(
                user=request.user, author=author)

            if not subscription.exists():
                return Response(
                    {'errors': 'Вы не подписаны'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get', 'delete'],
            url_path='subscriptions',
            pagination_class=Pagination,
            serializer_class=SubscriptionSerializer)
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user).all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RecipeTestViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeTestSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['author']
    pagination_class = Pagination

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=[IsAuthorOrReadOnly]
    )
    def generate_short_link(self, request, pk=None):
        id = get_object_or_404(Recipe, id=pk).id
        short_link = f'{settings.SITE_DOMAIN}/s/{id}'
        return Response({'short-link': short_link})

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthorOrReadOnly],
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                    user=user, recipes=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=user, recipes=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            try:
                cart_item = ShoppingCart.objects.get(
                    user=user,
                    recipes=recipe
                )
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response(
                    {'errors': 'Нету корзины с рецептом'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    def get_queryset(self):
        if self.request.user.is_authenticated:
            is_favorited = self.request.query_params.get('is_favorited')
            is_in_shopping_cart = self.request.query_params.get(
                'is_in_shopping_cart')
            if bool(is_favorited):
                return super().get_queryset().filter(
                    favourite__user=self.request.user)
            if bool(is_in_shopping_cart):
                return super().get_queryset().filter(
                    in_shopping_cart__user=self.request.user)
        if "tags" in self.request.query_params.keys():
            recipes = Recipe.objects.filter(
                tags__slug__in=dict(self.request.query_params)["tags"])
            return recipes
        return super().get_queryset()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticatedOrReadOnly],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        shopping_list = {}

        for item in shopping_cart:
            recipe = item.recipes
            for ingredient in recipe.ingredients.all():
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                amount = ingredient.amount
                if name in shopping_list:
                    shopping_list[name]['amount'] += amount
                else:
                    shopping_list[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount,
                    }

        content = '\n'.join(
            [f"{name} ({data['measurement_unit']}) — {data['amount']}"
             for name, data in shopping_list.items()]
        )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; '
            'filename="shopping_list.txt"'
        )
        return response

    @action(detail=True,
            methods=["post", "delete"],
            url_path="favorite",
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(
                {'errors': 'Нету такого рецепта'},
                status=status.HTTP_404_NOT_FOUND)
        if request.method == "POST":
            favourite, created = Favourite.objects.get_or_create(
                user=request.user, recipe=recipe)
            if not created:
                return Response(
                    {'errors': 'Уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                serializer = RecipeShortSerializer(recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED)
        else:
            try:
                favourite = Favourite.objects.get(
                    user=request.user,
                    recipe=recipe)
                favourite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Favourite.DoesNotExist:
                return Response(
                    {'errors': 'Нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST)
