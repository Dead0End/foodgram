import re
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest


def username_validation(username):
    if username.lower() == ('me'):
        raise ValidationError('такое имя нельзя использовать')
    pattern = re.compile(r'^[\w.@+-]+$')
    if not pattern.match(username):
        raise ValidationError(
            f'Username "{username}" does not match the required format.'
        )


def email_validation(email):
    if len(email) == '':
        return HttpResponseBadRequest('поле Email - обязательно')


def image_validation(image):
    file_size = image.file.size
    if file_size > 5 * 1024 * 1024:
        raise ValidationError('Файл не может быть более 5мб')
    valid_formats = ['.png', '.jpg', '.jpeg']
    if not any(image.name.endswith(fmt) for fmt in valid_formats):
        raise ValidationError('можно использовать только PNG, JPG, JPEG.')
