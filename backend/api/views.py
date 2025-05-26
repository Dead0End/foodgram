from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter
from recipes.models import (
    Favourite, Ingredient, Recipe, ShoppingCart, Subscription, Tag
)
from .pagination import Pagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer, IngredientSerializer, RecipeShortSerializer,
    RecipeTestSerializer, SubscriptionSerializer, TagSerializer, UserSerializer
)

User = get_user_model()


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    search_fields = ['name']
    http_method_names = ['get']
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    filterset_fields = ['name']
    serializer_class = IngredientSerializer


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    permission_class = (AllowAny)
    pagination_class = None
    queryset = Tag.objects.all()


class UserViewSet(DjoserUserViewSet):
    serializer_class = UserSerializer
    ordering = ('username')
    queryset = User.objects.all()
    pagination_class = Pagination

    @action(methods=['GET'],
            detail=False,
            permission_classes=[IsAuthenticated],)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        methods=['PUT'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar_put(self, request, *args, **kwargs):
        user = request.user
        serializer = AvatarSerializer(
            instance=user,
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @avatar_put.mapping.delete
    def avatar_delete(self, request, *args, **kwargs):
        user = request.user
        if not user.avatar:
            return Response(
                {'error': 'Аватар отсутствует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.avatar.delete()

        return Response(
            {'message': 'Аватар успешно удалён'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, pk=self.kwargs['id'])

        if request.method == "POST":
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscription, created = Subscription.objects.get_or_create(
                user=user,
                author=author
            )

            if not created:
                return Response(
                    {'errors': 'Вы уже подписаны'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscription = Subscription.objects.filter(
            user=request.user,
            author=author
        )

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

    def _add_to_relation(
            self,
            user,
            obj,
            relation_model,
            relation_field,
            error_message):
        """Общий метод для добавления в связь (корзину/избранное)."""
        relation, created = relation_model.objects.get_or_create(
            user=user,
            **{relation_field: obj}
        )
        if not created:
            return Response(
                {'errors': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = RecipeShortSerializer(obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_from_relation(self, user, obj, relation_model,
                              relation_field, error_message):
        """Общий метод для удаления из связи (корзины/избранного)."""
        try:
            relation = relation_model.objects.get(
                user=user,
                **{relation_field: obj}
            )
            relation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except relation_model.DoesNotExist:
            return Response(
                {'errors': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        methods=['post'],
        permission_classes=[IsAuthorOrReadOnly],
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        return self._add_to_relation(
            user=request.user,
            obj=recipe,
            relation_model=ShoppingCart,
            relation_field='recipes',
            error_message='Рецепт уже в корзине'
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        return self._remove_from_relation(
            user=request.user,
            obj=recipe,
            relation_model=ShoppingCart,
            relation_field='recipes',
            error_message='Нету корзины с рецептом'
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
            methods=["post"],
            url_path="favorite",
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(
                {'errors': 'Нету такого рецепта'},
                status=status.HTTP_404_NOT_FOUND)
        return self._add_to_relation(
            user=request.user,
            obj=recipe,
            relation_model=Favourite,
            relation_field='recipe',
            error_message='Уже в избранном'
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(
                {'errors': 'Нету такого рецепта'},
                status=status.HTTP_404_NOT_FOUND)
        return self._remove_from_relation(
            user=request.user,
            obj=recipe,
            relation_model=Favourite,
            relation_field='recipe',
            error_message='Нет в избранном'
        )
