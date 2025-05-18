import csv

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из CSV файла ingredients.csv'

    def handle(self, *args, **options):
        csv_file_path = 'backend/data/ingredients.csv'
        ingredients_to_create = []

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    try:
                        ingredients_to_create.append(
                            Ingredient(
                                name=row[0],
                                measurement_unit=row[1]
                            )
                        )
                    except IndexError:
                        self.stdout.write(self.style.ERROR(
                            f"Некорректный формат строки: {row}"))
                        continue
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f"Ошибка обработки строки {row}: {e}"))
                        continue
            created = Ingredient.objects.bulk_create(
                ingredients_to_create,
                ignore_conflicts=True
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Успешно импортировано {len(created)} ингредиентов'))

        except FileNotFoundError:
            raise CommandError(f'Файл "{csv_file_path}" не найден. '
                                'Убедитесь, что файл ingredients.csv находится в директории data/')
        except Exception as e:
            raise CommandError(f'Ошибка при импорте: {e}')