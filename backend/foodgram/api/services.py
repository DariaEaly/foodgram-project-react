import io
from collections import defaultdict

from recipes.models import RecipeIngredient


def create_shopping_list(user):
    lines = []
    recipe_ingredients = RecipeIngredient.objects.filter(
        recipe__shopping__user=user)
    ingredient_totals = defaultdict(int)

    for recipe_ingredient in recipe_ingredients:
        ingredient = recipe_ingredient.ingredient
        ingredient_name = f'{ingredient.name} ({ingredient.measurement_unit})'
        ingredient_totals[ingredient_name] += recipe_ingredient.amount
    for ingredient_name, amount_sum in ingredient_totals.items():
        lines.append(f'{ingredient_name} - {amount_sum}\n')

    return io.BytesIO(''.join(lines).encode())
