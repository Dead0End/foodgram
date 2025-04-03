from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField
from django.core.validators import MinValueValidator

from django.core.exceptions import ValidationError

from django.db import transaction
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer

from recipes.models import (Favourite,
                            Ingredient,
                            Recipe,
                            RecipeUser,
                            Tag,
                            Subscription,
                            RecipeItself,
                            RecipeIngredient)
from users.models import (CustomUser)

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email',]


class UserSerializer(UserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'avatar', 'is_subscribed']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.follower.filter(follow=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = CustomUser
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
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit')


class StandartRecipeSerializer(serializers.ModelSerializer):
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
            'cooking_time',
        )


class AuthorRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeUser
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


class IngridientCreateSerializer(IngridientSerializer):
    class Meta(IngridientSerializer.Meta):
        fields = ['name', 'measurement_unit']


class SubscriptionSerializer(serializers.ModelSerializer):
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
        return obj.author.recipes.count()

    def get_recipes(self, obj):
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

        return AuthorRecipeSerializer(
            recipes, many=True, context={'request': request}
        ).data


class RecipeReadSerializer(StandartRecipeSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    ingredients = IngridientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = serializers.IntegerField(validators=(MinValueValidator(1),))

    class Meta(StandartRecipeSerializer.Meta):
        fields = StandartRecipeSerializer.Meta.fields
        read_only_fields = ('author',)

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Вставьте изображение'
            )
        return image

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'поставьте минимум один тег'
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Не может быть двух одинаковых тегов')
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'поставьте минимум один ингридиент'
            )
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Не может быть двух одинаковых ингриддиентов'
            )
        return ingredients


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
            raise ValidationError('Нельзя пподписаться на самого себя')


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    ingredients = IngridientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = serializers.IntegerField(validators=(MinValueValidator(1),))

    class Meta(AuthorRecipeSerializer.Meta):
        fields = AuthorRecipeSerializer.Meta.fields

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                'Вставьте изображение'
            )
        return image

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                'поставьте минимум один тег'
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Не может быть двух одинаковых тегов')
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'поставьте минимум один ингридиент'
            )
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Не может быть двух одинаковых ингриддиентов'
            )
        return ingredients

    def create_ingredients(self, recipe, ingredients):
        RecipeItself.objects.bulk_create(
            RecipeItself(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = RecipeUser.objects.create(['pk'])
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def to_representation(self, instance):
        return RecipeCreateSerializer(instance, context=self.context).data


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient', queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeTestSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientSerializer(many=True)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            if len(ingredients_data) < 2:
                raise serializers.ValidationError('Нужно минимум два ингридиента и один тэг')

            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient_data['ingredient'], amount=ingredient_data['amount'])
        recipe.tags.set(tags_data)
        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        return representation

    class Meta:
        model = Recipe
        fields = '__all__'
