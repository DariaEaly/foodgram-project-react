from django.db.models import Exists, OuterRef, Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import UserCreateSerializer
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Follow, User

from .filters import RecipeFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, FollowSerializer,
                          RecipeGetSerializer, IngredientSerializer,
                          RecipePostSerializer, RecipeShortSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserSerializer, FollowGetSerializer)
from .services import create_shopping_list
from rest_framework.pagination import PageNumberPagination


class CustomUserViewSet(UserViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return User.objects.annotate(
                is_subscribed=Exists(
                    Follow.objects.filter(user=user, author=OuterRef('pk'))))
        return User.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipePostSerializer
        return RecipeGetSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return (Recipe.objects.select_related('author')
                    .prefetch_related('ingredients')
                    .annotate(
                        is_favorited=Exists(Favorite.objects.filter(
                            user=user, recipe=OuterRef('pk'))),
                        is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                            user=user, recipe=OuterRef('pk')))))
        return Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
        super(RecipeViewSet, self).perform_update(serializer)

    @action(['get'], detail=False)
    def download_shopping_cart(self, request):
        temp_file = create_shopping_list(request.user)
        temp_file.seek(0)
        response = FileResponse(temp_file, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; '
            'filename=shopping_list.txt'
        )
        return response


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class FollowView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk is None:
            follow = (Follow.objects.filter(user=request.user)
                      .prefetch_related('author'))
            authors = [follow_obj.author for follow_obj in follow]
            paginator = PageNumberPagination()
            paginator.page_size = 6
            result = paginator.paginate_queryset(authors, request)
            serializer = FollowGetSerializer(
                result, many=True, context={"current_user": request.user}
            )
            return paginator.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

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


class BaseRecipeView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeGetSerializer

    def function(self, request, pk, queryset, related_field, serializer):
        if request.method == 'GET':
            if pk is None:
                queryset = queryset.filter(
                    Q(**{f'{related_field}__user': request.user}))
                serializer = RecipeGetSerializer(queryset, many=True)
                return Response(serializer.data)
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if request.method == 'POST':
            data = {
                'user': request.user.id,
                'recipe': pk,
            }
            serializer = serializer(data=data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(
                    RecipeShortSerializer(
                        get_object_or_404(Recipe, id=pk)).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            added = queryset.filter(Q(user=request.user) & Q(recipe=recipe))
            if added.exists():
                added.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class FavoriteView(BaseRecipeView):
    def get(self, request, pk=None):
        return self.function(
            request, pk, queryset=Recipe.objects.all(),
            related_field='favorited', serializer=FavoriteSerializer)

    def post(self, request, pk):
        return self.function(
            request, pk, queryset=Recipe.objects.all(),
            related_field='favorited', serializer=FavoriteSerializer)

    def delete(self, request, pk):
        return self.function(
            request, pk, queryset=Favorite.objects.all(),
            related_field='favorited', serializer=FavoriteSerializer)


class ShoppingCartView(BaseRecipeView):
    def get(self, request, pk=None):
        return self.function(
            request, pk, queryset=Recipe.objects.all(),
            related_field='shopping', serializer=ShoppingCartSerializer)

    def post(self, request, pk):
        return self.function(
            request, pk, queryset=Recipe.objects.all(),
            related_field='shopping', serializer=ShoppingCartSerializer)

    def delete(self, request, pk):
        return self.function(
            request, pk, queryset=ShoppingCart.objects.all(),
            related_field='shopping', serializer=ShoppingCartSerializer)
