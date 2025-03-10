from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer

from recipes.models import (Favourite,
                            Ingridient,
                            Recipe,
                            RecipeItself,
                            Tag,
                            Subscription)

User = get_user_model()


class RecipeItselfSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeItself
        fields = '__all__'


class UserSerializer(UserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'avatar', 'is_subscribed']


    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.follower.filter(follow=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug'
        )


class IngridientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingridient
        fields = (
            'id',
            'name',
            'measurement_unit'
            )


class IngridientCreateSerializer(IngridientSerializer):

    class Meta(IngridientSerializer.Meta):
        fields = ['name', 'measurement_unit']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для представления подписок."""

    email = serializers.EmailField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='author.avatar')

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )
        read_only_fields = fields

    def get_recipes_count(self, obj):
        """Получение количества рецептов автора."""
        return obj.author.recipes.count()

    def get_recipes(self, obj):
        """Получение рецептов автора с учетом лимита."""
        request = self.context.get('request')
        if not request:
            return []

        recipes = obj.author.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except ValueError:
                pass

        return SubscribedRecipeSerializer(
            recipes, many=True, context={'request': request}
        ).data

class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = IngridientSerializer(
        many=True,
        source='recipe_ingredients'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('__all__')


class FollowerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favourite
        fields = '__all__'


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

class CreateSubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'
    
    def validation(self, data):
        user = self.context.get('request').user
        subscriber = data.get('subscriber')
        if user == subscriber:
            raise ValidationError('Нельзя пподписаться на себя')

