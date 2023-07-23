from django_filters.rest_framework import FilterSet, filters
from recipes.models import Ingredient, Recipe


class TagsFilter(filters.BaseCSVFilter, filters.CharFilter):
    pass


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')
    tags = TagsFilter(field_name='tags__slug', lookup_expr='in')

    class Meta:
        model = Recipe
        fields = {
            'author': ['exact'],
        }

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            user = self.request.user
            return queryset.filter(favorited__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            user = self.request.user
            return queryset.filter(shopping__user=user)
        return queryset


class IngredientFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
