import csv
import os
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from recipes.models import Tag

class Command(BaseCommand):
    help = 'Импортирует теги из CSV файла'

    def handle(self, *args, **options):
        csv_file_path = 'backend/data/tags.csv'
        
        # Проверка существования файла
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(
                f'Файл "{csv_file_path}" не найден. Текущая рабочая директория: {os.getcwd()}'))
            return

        tags_to_create = []
        try:
            with open(csv_file_path, mode='r', encoding='utf-8-sig') as csvfile:  # Изменена кодировка
                reader = csv.reader(csvfile)
                try:
                    next(reader)  # Пропускаем заголовок
                except StopIteration:
                    self.stdout.write(self.style.ERROR('Файл пуст'))
                    return

                for row_num, row in enumerate(reader, 2):  # Начинаем с 2, так как 1-я строка - заголовок
                    if not row:  # Пропускаем пустые строки
                        continue
                    try:
                        tag = Tag(
                            name=row[0],
                            slug=row[1],
                        )
                        tag.full_clean()  # Валидация перед сохранением
                        tags_to_create.append(tag)
                    except (ValidationError, IndexError) as e:
                        self.stdout.write(self.style.ERROR(
                            f"Ошибка обработки строки {row_num}: {row}. Ошибка: {e}"))
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
