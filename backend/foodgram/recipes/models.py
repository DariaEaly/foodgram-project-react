from colorfield.fields import ColorField
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Tag(models.Model):
    name = models.CharField('Название тега', unique=True, max_length=200,
                            help_text='Введите название тега')
    slug = models.SlugField('URL тега', unique=True,
                            help_text='Введите URL тега')
    color = ColorField(
        'Цвет', unique=True, help_text='Цветовой HEX-код тега')

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента', max_length=200,
        help_text='Введите название ингредиента')
    measurement_unit = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField('Название рецепта', max_length=200,
                            help_text='Введите название рецепта')
    image = models.ImageField(
        upload_to='recipes/images/',
    )
    text = models.TextField(
        'Текстовое описание',
        help_text='Напишите ваш рецепт')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Список ингредиентов',
        related_name='recipes',
        help_text='Выберите ингредиенты')
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
        help_text='Теги рецепта',
    )
    cooking_time = models.IntegerField(
        validators=(MinValueValidator(1),),
        verbose_name='Время приготовления (в минутах)')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favoriter',
        blank=True,
        null=True,)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited',
        blank=True,
        null=True,)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='unique_favorite')]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shopper',
        blank=True,
        null=True,)
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping',
        blank=True,
        null=True,)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                                               name='unique_shopping')]
