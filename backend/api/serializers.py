from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (User,
                            Follower,
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

    class Meta:
        model = User
        fields = '__all__'


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
        model = Follower
        fields = '__all__'
