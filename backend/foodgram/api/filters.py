from django_filters import rest_framework as drf_filters
from recipes.models import Ingredient, Recipe
from rest_framework import filters


class TagsFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        tags = request.query_params.getlist('tags')
        if tags:
            return queryset.filter(tags__slug__in=tags)
        return queryset


class RecipeFilter(drf_filters.FilterSet):
    is_favorited = drf_filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = drf_filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

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


class IngredientFilter(drf_filters.FilterSet):
    name = drf_filters.CharFilter(field_name='name', lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
