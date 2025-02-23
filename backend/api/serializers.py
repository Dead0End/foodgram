from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth.models import AnonymousUser

from recipes.models import (User,
                            Favourite,
                            Ingridient,
                            Recipe,
                            RecipeItself,
                            Tag)


class RecipeItselfSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient.name')
    measurment_unit = serializers.CharField(source='ingredient.measurment_unit')

    class Meta:
        model = RecipeItself
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.follower.filter(author=obj).exists()

    def to_representation(self, instance):
        request = self.context.get('request')
        if isinstance(request.user, AnonymousUser):
            return {
                'id': 0,
                'username': '',
                'first_name': '',
                'last_name': '',
                'email': '',
                'avatar': None,
                'is_subscribed': False
            }
        return super().to_representation(instance)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'avatar', 'is_subscribed']


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngridientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingridient
        ffields = '__all__'


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