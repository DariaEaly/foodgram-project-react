import io

from recipes.models import RecipeIngredient


def create_shopping_list(user):
    lines = []
    recipe_ingredients = RecipeIngredient.objects.filter(
        recipe__shopping__user=user)
    for recipe_ingredient in recipe_ingredients:
        ingredient = recipe_ingredient.ingredient
        lines.append(
            f'{ingredient.name} ({ingredient.measurement_unit})'
            f' - {recipe_ingredient.amount}\n')
    return io.BytesIO(''.join(lines).encode())
