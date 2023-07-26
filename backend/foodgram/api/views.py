from django.db.models import Exists, OuterRef, Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import UserCreateSerializer, SetPasswordSerializer
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import Follow, User

from .filters import RecipeFilter, IngredientFilter, TagsFilter
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, FollowSerializer,
                          RecipeGetSerializer, IngredientSerializer,
                          RecipePostSerializer, RecipeShortSerializer,
                          ShoppingCartSerializer, TagSerializer,
                          UserSerializer, FollowGetSerializer)
from .services import create_shopping_list
from rest_framework.pagination import PageNumberPagination


class UserViewSet(UserViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return (User
                    .objects
                    .annotate(
                        is_subscribed=Exists(
                            Follow.objects
                            .filter(user=user, author=OuterRef('pk'))
                            )
                        ))
        return User.objects.all()

    @action(['get'], detail=False)
    def subscriptions(self, request):
        follow = (Follow
                  .objects
                  .filter(user=request.user)
                  .prefetch_related('author'))
        authors = [follow_obj.author for follow_obj in follow]
        paginator = PageNumberPagination()
        paginator.page_size = 6
        result = paginator.paginate_queryset(authors, request)
        serializer = FollowGetSerializer(
            result, many=True, context={"user": request.user}
        )
        for author_data in serializer.data:
            author_data["is_subscribed"] = author_data["id"] in (
                [author.id for author in authors])

        return paginator.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True, url_path='subscribe')
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            data = {
                'user': request.user.id,
                'author': id,
            }
            serializer = FollowSerializer(
                data=data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(UserSerializer(author).data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            del_count, _ = author.following.filter(user=request.user).delete()
            if del_count:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend, TagsFilter)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipePostSerializer
        return RecipeGetSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = (Recipe
                    .objects
                    .select_related('author')
                    .prefetch_related('ingredients')
                    )
        if user.is_authenticated:
            return (queryset
                    .annotate(
                     is_favorited=Exists(
                        Favorite.objects
                        .filter(user=user, recipe=OuterRef('pk'))),
                     is_in_shopping_cart=Exists(
                        ShoppingCart.objects
                        .filter(user=user, recipe=OuterRef('pk'))))
                    )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
        super(RecipeViewSet, self).perform_update(serializer)

    @classmethod
    def manage_user_recipe_relations(
            cls, request, pk, queryset, related_field, serializer):
        """
        Обрабатывает просмотр рецептов,
        добавление и удаление cвязанных объектов).
        """
        if request.method == 'GET':
            if pk is None:
                queryset = (queryset
                            .filter(
                                **{f'{related_field}__user': request.user}))
                serializer = RecipeGetSerializer(queryset, many=True)
                return Response(serializer.data)
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if request.method == 'POST':
            data = {
                'user': request.user.id,
                'recipe': pk,
            }
            serializer = serializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(RecipeShortSerializer(
                get_object_or_404(Recipe, id=pk)).data,
                status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            del_count, _ = (queryset
                            .filter(
                                Q(user=request.user)
                                & Q(recipe=recipe)).delete())
            if del_count:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        return self.manage_user_recipe_relations(
            request, pk, queryset=Favorite.objects.all(),
            related_field='favorited', serializer=FavoriteSerializer)

    @action(['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        return self.manage_user_recipe_relations(
            request, pk, queryset=ShoppingCart.objects.all(),
            related_field='shopping', serializer=ShoppingCartSerializer)

    @action(['get'], detail=False)
    def download_shopping_cart(self, request):
        temp_file = create_shopping_list(request.user)
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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
