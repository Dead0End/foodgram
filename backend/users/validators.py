import re
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError

class UsernameValidator(UnicodeUsernameValidator):
    def __call__(self, value: str) -> None:
        if not re.match(r'^[\w@+-]+\Z', value):  # Совпадает с ожидаемым в тестах
            raise ValidationError(
                'Username может содержать только буквы, цифры и @/+/-/_.'
            )
        super().__call__(value)  # Дополнительно проверяем стандартные правила
