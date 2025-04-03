from rest_framework import status, mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from django.db.models import Sum

from .pagination import Pagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    UserSerializer,
    IngridientSerializer,
    IngridientCreateSerializer,
    TagSerializer,
    AvatarSerializer,
    SubscriptionSerializer,
    RecipeTestSerializer
)
from recipes.models import (
    Ingredient,
    Recipe,
    Tag,
    Subscription
)
User = get_user_model()


class IngridientViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    search_fields = ['name']
    http_method_names = ['get']
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['name']

    def get_serializer_class(self):
        if self.action in ['create']:
            return IngridientCreateSerializer
        return IngridientSerializer


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

    @action(detail=True, methods=['post'], url_path='subscribe')
    def subscribe(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, pk=self.kwargs['id'])

        if user == author:
            return Response({'errors': 'Нелльзя подписаться на себя'}, status=status.HTTP_400_BAD_REQUEST)

        if Subscription.objects.filter(user=user, author=author).exists():
            return Response({'errors': 'Вы уже подписаны'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            subscription = Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Ошибка при создании подписки: {e}")
            return Response({'errors': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'], url_path='subscriptions')
    def subscriptions(self, request, pk=None):
        subscription_list = Subscription.get_object(all)
        return subscription_list

    @action(detail=True, methods=['delete'], url_path='unsubscribe')
    def unsubscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        subscription = Subscription.objects.filter(user=request.user, author=author)

        if not subscription.exists():
            return Response(
                {'errors': 'Вы не подписаны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeTestSerializer
    filter_backends = (DjangoFilterBackend,)
    open_actions = {'list', 'retrieve', 'get_link'}
    authenticated_actions = {
        'create',
        'favorite',
        'shopping_cart',
        'download_shopping_cart',
    }
    restricted_actions = {'update', 'partial_update', 'destroy'}
    restricted_permission = IsAuthorOrReadOnly

    def handle_action(
        self, request, pk, related_name, add_error, remove_error
    ):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        related_manager = getattr(user, related_name)
        if request.method == 'POST':
            if related_manager.filter(id=recipe.id).exists():
                raise ValidationError(add_error)
            related_manager.add(recipe)
            serializer = RecipeTestSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not related_manager.filter(id=recipe.id).exists():
            raise ValidationError(remove_error)
        related_manager.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('POST', 'DELETE'), detail=True, url_path='favorite')
    def favorite(self, request, pk=None):
        return self._handle_action(
            request,
            pk,
            'favorite_recipes',
            'Рецепт уже избранном',
            'Рецепта нет в избранном',
        )

    @action(methods=('POST', 'DELETE'), detail=True, url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        return self._handle_action(
            request,
            pk,
            'shopping_cart',
            'Рецепт уже в списке покупок.',
            'Рецепта нет в списке покупок.',
        )

    @action(
        methods=('GET',),
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart_recipes = (
            user.shopping_cart.prefetch_related(
                'recipe_ingredients__ingredient'
            )
            .values(
                'recipe_ingredients__ingredient__name',
                'recipe_ingredients__ingredient__measurement_unit',
            )
            .annotate(total_amount=Sum('recipe_ingredients__amount'))
        )
        if not shopping_cart_recipes:
            return Response(
                {'detail': 'Список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RecipeTestViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeTestSerializer
    permission_classes=[IsAuthenticated, IsAuthorOrReadOnly]
