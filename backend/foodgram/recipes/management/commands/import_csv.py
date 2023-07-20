import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует данные из csv файлов'

    def handle(self, *args, **options):
        with open(
            '../../data/ingredients.csv',
             encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=',')
            for row in csv_reader:
                name = row['name']
                measurement_unit = row['measurement_unit']
                Ingredient(
                    name=name,
                    measurement_unit=measurement_unit).save()
