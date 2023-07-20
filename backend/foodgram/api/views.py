from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import UserCreateSerializer
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User

from .filters import RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, FollowSerializer,
                          PasswordUserSerializer, RecipeGetSerializer,
                          RecipeIngredientSerializer, RecipePostSerializer,
                          RecipeShortSerializer, ShoppingCartSerializer,
                          TagSerializer, UserSerializer)


class CustomUserViewSet(UserViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        return User.objects.all()

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = PasswordUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecipePostSerializer
        return RecipeGetSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeGetSerializer(instance=serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
        super(RecipeViewSet, self).perform_update(serializer)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = RecipeIngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name')
    permission_classes = [IsAdminOrReadOnly]


class FollowListView(generics.ListAPIView):
    serializer_class = RecipeGetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(
            author__following__user_id=self.request.user.id)


class FavoriteListView(generics.ListAPIView):
    serializer_class = RecipeGetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(
            favorited__user_id=self.request.user)


class FollowUnfollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        data = {
            'user': request.user.id,
            'author': pk,
        }
        serializer = FollowSerializer(
            data=data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                UserSerializer(User.objects.get(pk=pk)).data,
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        author = get_object_or_404(User, id=pk)
        following = author.following.filter(user=request.user)
        if following.exists():
            following.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status.HTTP_400_BAD_REQUEST)


class FavoriteCreateDestroyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk,
        }
        serializer = FavoriteSerializer(
            data=data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                RecipeShortSerializer(get_object_or_404(Recipe, id=pk)).data,
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = recipe.favorited.filter(user=request.user)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status.HTTP_400_BAD_REQUEST)


class ShoppinCartListView(generics.ListAPIView):
    serializer_class = RecipeGetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(
           shopping__user_id=self.request.user.id)


class ShoppingCartAdd(APIView):
    def post(self, request, pk):
        data = {
            'user': request.user.id,
            'recipe': pk,
        }
        serializer = ShoppingCartSerializer(
            data=data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                RecipeShortSerializer(get_object_or_404(Recipe, id=pk)).data,
                status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        shopping = recipe.shopping.filter(user=request.user)
        if shopping.exists():
            shopping.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status.HTTP_400_BAD_REQUEST)


def download_shopping(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=shopping_list.txt'
    recipes = Recipe.objects.filter(shopping__user_id=request.user.id)
    lines = []
    for recipe in recipes:
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient.ingredient
            lines.append(
                f'{ingredient.name} ({ingredient.measurement_unit})'
                f' - {recipe_ingredient.amount}\n'
            )
    response.writelines(lines)
    return response
