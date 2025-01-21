from django.core.exceptions import ValidationError

def username_validation(username):
    if username.lower() == 'me':
        raise ValidationError(f'такое имя нельзя использовать')


def image_validation(image):
    file_size = image.file.size
    if file_size > 5 * 1024 * 1024:
        raise ValidationError(f'Файл не может быть более 5мб')
    valid_formats = ['.png', '.jpg', '.jpeg']
    if not any(image.name.endswith(fmt) for fmt in valid_formats):
        raise ValidationError('можно использовать только PNG, JPG, JPEG.')