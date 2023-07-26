import base64

from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserSerializer
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Follow, User


class TagSerializer(serializers.ModelSerializer):
    color = serializers.CharField(required=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class UserSerializer(UserSerializer):
    is_subscribed = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        read_only=True, many=True, source='recipeingredient_set')
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.BooleanField(default=False, read_only=True)
    is_in_shopping_cart = serializers.BooleanField(
        default=False, read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart')


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time')


class RecipePostSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault())
    image = Base64ImageField()
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(), slug_field='id', many=True)

    class Meta:
        model = Recipe
        fields = (
            'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time')

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance, context={'request': self.context.get('request')}).data

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        ingredients_create = []
        for ingredient in ingredients:
            ingredients_create.append(
                RecipeIngredient(
                    ingredient=ingredient['id'], recipe=recipe,
                    amount=ingredient['amount']))
        RecipeIngredient.objects.bulk_create(ingredients_create)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        ingredients = validated_data.pop('ingredients')
        instance.recipeingredient_set.all().delete()
        ingredients_create = []
        for ingredient in ingredients:
            ingredients_create.append(
                RecipeIngredient(
                    ingredient=ingredient['id'], recipe=instance,
                    amount=ingredient['amount']))
        RecipeIngredient.objects.bulk_create(ingredients_create)
        instance.save()
        return instance


class FollowGetSerializer(UserSerializer):
    recipes = RecipeShortSerializer(many=True)
    author = UserSerializer
    recipes_count = serializers.SerializerMethodField("get_recipes_count")
    is_subscribed = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        ]

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    author = UserSerializer

    class Meta:
        model = Follow
        fields = ('author', 'user')

        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            )
        ]

    def validate(self, data):
        if self.context['request'].user == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя')
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='id',
        default=serializers.CurrentUserDefault())
    recipe = RecipeGetSerializer

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='id',
        default=serializers.CurrentUserDefault())
    recipe = RecipeGetSerializer

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]
