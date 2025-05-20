import csv

from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из CSV файла'

    def handle(self, *args, **options):
        csv_file_path = 'backend/data/ingredients.csv'
        ingredients_to_create = []
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    try:
                        ingredient = Ingredient(
                            name=row[0],
                            measurement_unit=row[1]
                        )
                        ingredients_to_create.append(ingredient)
                    except (ValidationError, IndexError) as e:
                        self.stdout.write(self.style.ERROR(
                            f"Ошибка обработки строки {row}: {e}"))
                        continue
            created_ingredients = Ingredient.objects.bulk_create(
                ingredients_to_create,
                ignore_conflicts=True
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно импортировано {len(created_ingredients)} ингредиентов'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(
                f'Файл "{csv_file_path}" не найден.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'Ошибка при обработке файла: {e}'))
