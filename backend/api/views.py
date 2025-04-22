from rest_framework import status, mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
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
    Subscription,
    ShoppingCart
)
from api.filters import IngredientFilter

User = get_user_model()


class IngridientViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    search_fields = ['name']
    http_method_names = ['get']
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
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
            return Response({'errors': 'Нельзя подписаться на себя'}, status=status.HTTP_400_BAD_REQUEST)

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


class RecipeTestViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeTestSerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        perission_classes = [IsAuthenticated]

    )
    def generate_short_link(self, request, pk=None):
        id = get_object_or_404(Recipe, id=pk).id
        short_link = f'{settings.SITE_DOMAIN}/s/{id}'
        return Response({'short-link': short_link})

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        shopping_cart = ShoppingCart.objects.filter(user=user)
        shopping_list = {}

        for item in shopping_cart:
            recipe = item.recipes
            for ingredient in recipe.recipe_ingredients.all():
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