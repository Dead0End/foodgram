from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.db import transaction

from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favourite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeItself,
    RecipeUser,
    ShoppingCart,
    Subscription,
    Tag
)
from users.models import CustomUser

User = get_user_model()


class UserSerializer(UserSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.follower.filter(follow=obj).exists()

    class Meta:
        model = CustomUser
        fields = ['id',
                  'username',
                  'first_name',
                  'last_name',
                  'email',
                  'avatar',
                  'is_subscribed']


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
            'cooking_time',
        )


class BasicRecipeSerializer(serializers.ModelSerializer):
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

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).all().count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request:
            return []

        recipes = Recipe.objects.filter(author=obj.author).all()
        recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except ValueError:
                pass

        return BasicRecipeSerializer(
            recipes, many=True, context={'request': request}
        ).data

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


class RecipeReadSerializer(RecipeSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    ingredients = IngridientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(1),))

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
            raise serializers.ValidationError(
                'Не может быть двух одинаковых тегов')
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

    def to_representation(self, instance):
        representation = super().to_representation(instance).data
        return representation

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields
        read_only_fields = ('author',)


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

    def validation(self, data):
        user = self.context.get('request').user
        subscriber = data.get('subscriber')
        if user == subscriber:
            raise ValidationError('Нельзя пподписаться на самого себя')

    class Meta:
        model = Subscription
        fields = '__all__'


class RecipeCreateSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = Base64ImageField(required=True)
    ingredients = IngridientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(1),))

    class Meta(BasicRecipeSerializer.Meta):
        fields = BasicRecipeSerializer.Meta.fields

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
            raise serializers.ValidationError(
                'Не может быть двух одинаковых тегов')
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
                name=ingredient['name'],
                measurement_unit=ingredient['measurement_unit'],
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
        recipe.save()
        self.create_ingredients(recipe, ingredients)
        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance).data
        return representation


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(required=True)
    name = serializers.StringRelatedField(
        source='ingredient.name', required=False)
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit', required=False)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount', 'name', 'measurement_unit']


class RecipeTestSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientSerializer(many=True)
    author = UserSerializer(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = kwargs.get('context').get('request')

    def create(self, validated_data):
        try:
            ingredients_data = validated_data.pop('ingredients')
            tags_data = validated_data.pop('tags')
        except KeyError:
            raise serializers.ValidationError("Нету тегов или ингридиентов")
        image = validated_data['image']
        print(image)
        if not image:
            raise serializers.ValidationError('Нету изображения')
        if not len(ingredients_data):
            raise serializers.ValidationError('Нету ингридиентов')
        if not tags_data:
            raise serializers.ValidationError('Нету тегов')
        if len(list(tags_data)) != len(set(tags_data)):
            raise serializers.ValidationError('Теги повторяются')
        recipe = Recipe.objects.create(**validated_data,
                                       author=self.request.user)
        recipe.tags.set(tags_data)
        ids = []
        for ingredient_data in ingredients_data:
            if ingredient_data['amount'] < 1:
                raise serializers.ValidationError('Нету ингридиента')
            if ingredient_data['ingredient'].pk in ids:
                raise serializers.ValidationError('Ингридиенты повторяются')
            ids.append(ingredient_data['ingredient'].pk)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount'])
        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        try:
            ingredients_data = validated_data.pop('ingredients')
            tags_data = validated_data.pop('tags')
        except KeyError:
            raise serializers.ValidationError("Нету тегов или ингридиентов")
        image = validated_data['image']
        recipe = instance
        if not image:
            raise serializers.ValidationError('Нету изображения')
        if not len(ingredients_data):
            raise serializers.ValidationError('Нету ингридиентов')
        ids = []
        for ingredient_data in ingredients_data:
            if ingredient_data['amount'] < 1:
                raise serializers.ValidationError('Нету ингридиента')
            if ingredient_data['ingredient'].pk in ids:
                raise serializers.ValidationError('Ингридиенты повторяются')
            ids.append(ingredient_data['ingredient'].pk)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount'])
        if not tags_data:
            raise serializers.ValidationError('Нету тегов')
        if len(list(tags_data)) != len(set(tags_data)):
            raise serializers.ValidationError('Теги повторяются')
        recipe.tags.set(tags_data)
        recipe.save()
        return super().update(
            instance=instance, validated_data=validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        if self.request.user.is_authenticated:
            representation[
                'is_favorited'] = Favourite.objects.filter(
                user=self.request.user, recipe=instance).exists()
            representation[
                'is_in_shopping_cart'] = ShoppingCart.objects.filter(
                user=self.request.user, recipes=instance).exists()
        else:
            representation['is_favorited'] = False
            representation['is_in_shopping_cart'] = False
        return representation

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
