from django.contrib import admin
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'


class IngredientsInLine(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'text', 'author', 'pub_date', 'get_tags')
    search_fields = ('text', 'name')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    inlines = [
        IngredientsInLine,
    ]

    def get_tags(self, obj):
        return "\n".join([p.name for p in obj.tags.all()])


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user')
    search_fields = ('author', 'user')
    empty_value_display = '-пусто-'
    list_filter = ('author', 'user')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(ShoppingCart)
class ShoopingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', "id")
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_filter = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
