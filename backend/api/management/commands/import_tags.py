import csv

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Импортирует теги из CSV файла'

    def handle(self, *args, **options):
        csv_file_path = 'backend/data/tags.csv'
        tags_to_create = []
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)
                for row in reader:
                    try:
                        tag = Tag(
                            name=row[0],
                            slug=row[1],
                        )
                        tags_to_create.append(tag)
                    except (ValidationError, IndexError) as e:
                        self.stdout.write(self.style.ERROR(
                            f"Ошибка обработки строки {row}: {e}"))
                        continue
            created_tags = Tag.objects.bulk_create(
                tags_to_create,
                ignore_conflicts=True
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно импортировано {len(created_tags)} тегов'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'Файл "{csv_file_path}" не найден.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при обработке файла: {e}'))
