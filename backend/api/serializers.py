from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer

from recipes.models import (Favourite,
                            Ingridient,
                            Recipe,
                            RecipeItself,
                            Tag)

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