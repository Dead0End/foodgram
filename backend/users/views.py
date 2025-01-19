from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from api.serializers import CustomUserSerializer

User = get_user_model()


class CustomUser(UserViewSet):
    serializer = CustomUserSerializer
