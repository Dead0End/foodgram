from djoser.serializers import UserCreateSerializer
from django.cntrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Ingredient, Tag

User = get_user_model()


class CustUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password')


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ShortSerializer(ModelSerializer):
    image = Base64ImageField()
