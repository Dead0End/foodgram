from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model

from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Subscription,
    Tag,
)
from users.models import CustomUser

User = get_user_model()


class UserSerializer(UserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request is not None
                and request.user.is_authenticated
                and request.user.follower.filter(follow=obj).exists())

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'avatar',
            'is_subscribed'
        ]


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
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(default=True, read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
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
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request:
            return []

        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except ValueError:
                pass

        return RecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data


class RecipeReadSerializer(RecipeSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    ingredients = IngridientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields
        read_only_fields = ('author',)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True, required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate_avatar(self, value):
        if value is None:
            raise serializers.ValidationError("Аватар не может быть пустым")
        if hasattr(value, 'size') and value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Размер файла не должен превышать 2MB")
        return value

    def update(self, instance, validated_data):
        if 'avatar' not in validated_data:
            raise serializers.ValidationError({"avatar": "Это поле обязательно"})
        return super().update(instance, validated_data)


class CreateSubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('subscriber',)

    def validate(self, data):
        user = self.context['request'].user
        author = data['author']
        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя')
        if Subscription.objects.filter(subscriber=user, author=author).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя')
        return data

    def create(self, validated_data):
        validated_data['subscriber'] = self.context['request'].user
        return super().create(validated_data)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(required=True)
    name = serializers.StringRelatedField(
        read_only=True,
        source='ingredient.name',
        required=False)
    measurement_unit = serializers.StringRelatedField(
        read_only=True,
        source='ingredient.measurement_unit',
        required=False)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount', 'name', 'measurement_unit']


class RecipeTestSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, data):
        if not data.get('image'):
            raise serializers.ValidationError({'image': 'Изображение обязательно'})
        tags = data.get('tags', [])
        if not tags:
            raise serializers.ValidationError({'tags': 'Необходимо указать хотя бы один тег'})
        if len(tags) != len(set(tag.id for tag in tags)):
            raise serializers.ValidationError({'tags': 'Теги не должны повторяться'})
        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError({'ingredients': 'Необходимо указать хотя бы один ингредиент'})
        ingredient_ids = [ingredient['ingredient'].id for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError({'ingredients': 'Ингредиенты не должны повторяться'})
        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise serializers.ValidationError({
                    'ingredients': f"Количество ингредиента {ingredient['ingredient'].name} должно быть больше 0"
                })
        return data

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user
        )
        recipe.tags.set(tags_data)
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        instance.tags.set(tags_data)
        instance.ingredients.clear()
        recipe_ingredients = [
            RecipeIngredient(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        if self.request.user.is_authenticated:
            representation[
                'is_favorited'] = Favorite.objects.filter(
                user=self.request.user, recipe=instance).exists()
            representation[
                'is_in_shopping_cart'] = ShoppingCart.objects.filter(
                user=self.request.user, recipes=instance).exists()
        else:
            representation['is_favorited'] = False
            representation['is_in_shopping_cart'] = False
        return representation


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
