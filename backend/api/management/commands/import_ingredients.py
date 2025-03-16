import csv
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Импортирует ингредиенты из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV файлу с ингредиентами')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        imported_ingredients = []

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    try:
                        ingredient = Ingredient(
                            name=row[0],
                            measurement_unit=row[1]
                        )
                        ingredient.save()
                        imported_ingredients.append({
                            ingredient.id,
                            ingredient.name,
                            ingredient.measurement_unit
                        })
                    except ValidationError as e:
                        self.stdout.write(self.style.ERROR(f"Ошибка валидации строки {row}: {e}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Ошибка обработки строки {row}: {e}"))
        except FileNotFoundError:
            raise CommandError(f'Файл "{csv_file_path}" не найден.')
        except Exception as e:
            raise CommandError(f'Ошибка при открытии файла: {e}')

        self.stdout.write(self.style.SUCCESS(f'Импортированные ингредиенты: {imported_ingredients}'))