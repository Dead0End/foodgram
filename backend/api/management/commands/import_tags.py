import csv

from django.core.management.base import BaseCommand, CommandError
from recipes.models import Tag

from django.core.exceptions import ValidationError


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV файлу с ингредиентами')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        imported_tags = []

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    try:
                        tag = Tag(
                            name=row[0],
                            slug=row[0]
                        )
                        tag.save()
                        imported_tags.append({
                            tag.name,
                            tag.slug,
                        })
                        self.stdout.write(self.style.SUCCESS(f'Успешно импортирован ингредиент: {tag.name}'))
                    except ValidationError as e:
                        self.stdout.write(self.style.ERROR(f"Ошибка валидации строки {row}: {e}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Ошибка обработки строки {row}: {e}"))
        except FileNotFoundError:
            raise CommandError(f'Файл "{csv_file_path}" не найден.')
        except Exception as e:
            raise CommandError(f'Ошибка при открытии файла: {e}')

        self.stdout.write(self.style.SUCCESS(f'Импортированные ингредиенты: {imported_tags}'))