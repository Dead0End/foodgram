from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
)
from users.models import (
    Follower
)

User = get_user_model()


class UserSerializer(UserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.follower.filter(follow=obj).exists())

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'avatar', 'is_subscribed'
        ]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and obj.favorites.filter(user=request.user).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and obj.shopping_carts.filter(user=request.user).exists())

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time'
        )

    def _validate_ingredients_and_tags(self, data):
        """Общая валидация для ингредиентов и тегов"""
        tags = data.get('tags', [])
        ingredients = data.get('ingredients', [])
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Добавьте хотя бы один тег'})
        if len(tags) != len(set(tag.id for tag in tags)):
            raise serializers.ValidationError({
                'tags': 'Теги не должны повторяться'})
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Добавьте хотя бы один ингредиент'})
        ingredient_ids = [
            ingredient['ingredient'].id for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты не должны повторяться'})
        return data

    def validate(self, data):
        """Общая валидация"""
        return self._validate_ingredients_and_tags(data)

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])

    @transaction.atomic
    def create(self, validated_data):
        try:
            ingredients_data = validated_data.pop('ingredients')
            tags_data = validated_data.pop('tags')
        except KeyError:
            raise serializers.ValidationError("Нету тегов или ингридиентов")
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('юзер не аутентифицирован')

        image = validated_data['image']
        if not image:
            raise serializers.ValidationError('Нету изображения')
        if not ingredients_data:
            raise serializers.ValidationError('Нету ингридиентов')
        if not tags_data:
            raise serializers.ValidationError('Нету тегов')
        if len(list(tags_data)) != len(set(tags_data)):
            raise serializers.ValidationError('Теги повторяются')

        recipe = Recipe.objects.create(**validated_data, author=request.user)
        recipe.tags.set(tags_data)

        ids = []
        for ingredient_data in ingredients_data:
            if ingredient_data['ingredient'].pk in ids:
                raise serializers.ValidationError('Ингридиенты повторяются')
            ids.append(ingredient_data['ingredient'].pk)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount'])
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        image = validated_data['image']
        if not image:
            raise serializers.ValidationError('Нету изображения')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_ingredients(instance, ingredients)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class AuthorRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User, Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'author'
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='follow.email')
    id = serializers.IntegerField(source='follow.id')
    username = serializers.CharField(source='follow.username')
    first_name = serializers.CharField(source='follow.first_name')
    last_name = serializers.CharField(source='follow.last_name')
    is_subscribed = serializers.BooleanField(default=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='follow.avatar')

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.follow).all().count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request:
            return []

        recipes = Recipe.objects.filter(author=obj.follow).all()
        recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except ValueError:
                pass

        return AuthorRecipeSerializer(
            recipes, many=True, context={'request': request}
        ).data

    class Meta:
        model = Follower
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


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
