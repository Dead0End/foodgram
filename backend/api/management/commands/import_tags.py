import csv
import os
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Импортирует теги из CSV файла'

    def handle(self, *args, **options):
        csv_file_path = 'backend/data/tags.csv'
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(
                f'"{csv_file_path}" не найден сейчас: {os.getcwd()}'))
            return
        tags_to_create = []
        try:
            with open(
                csv_file_path,
                mode='r',
                encoding='utf-8-sig') as csvfile:
                reader = csv.reader(csvfile)
                try:
                    next(reader)
                except StopIteration:
                    self.stdout.write(self.style.ERROR('Файл пуст'))
                    return
                for row_num, row in enumerate(reader, 2):
                    if not row:
                        continue
                    try:
                        tag = Tag(
                            name=row[0],
                            slug=row[1],
                        )
                        tag.full_clean()
                        tags_to_create.append(tag)
                    except (ValidationError, IndexError) as e:
                        self.stdout.write(self.style.ERROR(
                            f"Ошибка {row_num}: {row}. Ошибка: {e}"))
                        continue
            created_tags = Tag.objects.bulk_create(
                tags_to_create,
                ignore_conflicts=True
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно импортировано {len(created_tags)} тегов'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при обработке файла: {e}'))
