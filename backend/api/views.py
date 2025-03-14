from rest_framework import status, mixins, viewsets, generics
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
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
    TagSerializer,
    AvatarSerializer,
    SubscriptionSerializer,
    CreateSubscribeSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer
)
from recipes.models import (
    Ingridient,
    Recipe,
    Tag,
    Subscription
)
from users.models import(
    CustomUser
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
        subscription_list = subscriptions.get_object(all)
        return subscription_list

    @action(detail=True, methods=['delete'], url_path='unsubscribe')
    def unsubscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        subscription = Subscribe.objects.filter(user=request.user, author=author)

        if not subscription.exists():
            return Response(
                {'errors': 'Вы не подписаны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RecipeViewSet(UserViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateSerializer
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
    serializer_map = {'get': RecipeReadSerializer}
    default_serializer = RecipeCreateSerializer

    def _handle_action(
        self, request, pk, related_name, add_error, remove_error
    ):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        author = get_object_or_404(User, pk=self.kwargs['id'])
        related_manager = getattr(user, related_name)
        if request.method == 'POST':
            if related_manager.filter(id=recipe.id).exists():
                raise ValidationError(add_error)
            related_manager.add(recipe)
            serializer = RecipeShortSerializer(
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
        detail=True,
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        return JsonResponse(
            {
                'short-link': generate_short_link(
                    get_object_or_404(Recipe, id=pk).id,
                    request.build_absolute_uri('/'),
                )
            },
            status=status.HTTP_200_OK,
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
        ingredients = {
            (
                item['recipe_ingredients__ingredient__name'],
                item['recipe_ingredients__ingredient__measurement_unit'],
            ): item['total_amount']
            for item in shopping_cart_recipes
        }
        return FileResponse(
            generate_shopping_list_pdf(ingredients),
            as_attachment=True,
            filename='shopping_list_{}_{}.pdf'.format(
                user.username, datetime.now().strftime("%Y-%m-%d")
            ),
        )
