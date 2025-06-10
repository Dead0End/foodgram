from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.http import require_GET
from djoser.views import UserViewSet as DjoserUserViewSet

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from recipes.models import (
    Favourite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from users.models import Follower
from .pagination import Pagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer, IngredientSerializer, RecipeShortSerializer,
    RecipeCreateSerializer, RecipeReadSerializer, SubscriptionSerializer,
    TagSerializer, UserSerializer
)

User = get_user_model()


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    search_fields = ['name']
    http_method_names = ['get']
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    serializer_class = IngredientSerializer


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    queryset = Tag.objects.all()


class UserViewSet(DjoserUserViewSet):
    serializer_class = UserSerializer
    ordering = ('username',)
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
            follower, created = Follower.objects.get_or_create(
                user=user,
                follow=author
            )
            if not created:
                return Response(
                    {'errors': 'Вы уже подписаны'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscriptionSerializer(
                author, context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        deleted_count = Follower.objects.filter(
            user=request.user,
            follow=author
        ).delete()[0]
        if deleted_count == 0:
            return Response(
                {'errors': 'Вы не подписаны'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            url_path='subscriptions',
            pagination_class=Pagination)
    def subscriptions(self, request):
        authors = User.objects.filter(
            follow__user=request.user
        )
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeReadSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def _handle_recipe_action(self, user, recipe, model_class, action_type):
        """Общий метод для добавления/удаления рецепта в избранное/корзину."""
        if action_type == 'add':
            obj, created = model_class.objects.get_or_create(
                user=user,
                **{'recipe' if model_class == Favourite else 'recipes': recipe}
            )
            if not created:
                return Response(
                    {'errors': f'уже есть{model_class._meta.verbose_name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        deleted_count = model_class.objects.filter(
            user=user,
            **{'recipe' if model_class == Favourite else 'recipes': recipe}
        ).delete()[0]
        if deleted_count == 0:
            return Response(
                {'errors': f'нету{model_class._meta.verbose_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        action_type = 'add' if request.method == 'POST' else 'remove'
        return self._handle_recipe_action(
            request.user, recipe, ShoppingCart, action_type)

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=[AllowAny],
        url_path='get-link',
        url_name='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        rev_link = reverse('short_url', args=[recipe.pk])
        absolute_uri = request.build_absolute_uri(
            rev_link).replace('http://', 'https://')
        return Response({'short-link': absolute_uri},
                        status=status.HTTP_200_OK,)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        content = '\n'.join(
            [f"{item['ingredient__name']} "
             f"({item['ingredient__measurement_unit']}) — "
             f"{item['total_amount']}"
             for item in ingredients]
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
        recipe = get_object_or_404(Recipe, pk=pk)
        action_type = 'add' if request.method == 'POST' else 'remove'
        return self._handle_recipe_action(
            request.user, recipe, Favourite, action_type)


@require_GET
def short_url(request, pk):
    try:
        Recipe.objects.filter(pk=pk).exists()
        return redirect(f'/recipes/{pk}/')
    except Exception:
        raise ValidationError(f'Recipe "{pk}" does not exist.')
