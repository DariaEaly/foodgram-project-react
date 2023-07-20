from django_filters import rest_framework as filters
from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')
    tags__slug = filters.MultipleChoiceFilter(
        field_name='tags__slug',
        lookup_expr='in',
        conjoined=True,
    )

    class Meta:
        model = Recipe
        fields = {
            'author': ['exact'],
        }

    def filter_is_favorited(self, queryset, name, value):
        if value:
            user = self.request.user
            return queryset.filter(favorited__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            user = self.request.user
            return queryset.filter(shopping__user=user)
        return queryset
