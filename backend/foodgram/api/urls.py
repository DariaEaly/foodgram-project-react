from api.views import (CustomUserViewSet, FavoriteCreateDestroyView,
                       FavoriteListView, FollowListView, FollowUnfollowView,
                       IngredientViewSet, RecipeViewSet, ShoppinCartListView,
                       ShoppingCartAdd, TagViewSet, download_shopping)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('recipes/download_shopping_cart/',
         download_shopping, name='download_shopping_cart'),
    path('recipes/<int:pk>/shopping_cart/',
         ShoppingCartAdd.as_view(), name='add_shopping_cart'),
    path('recipes/shopping_cart/',
         ShoppinCartListView.as_view(), name='shopping_cart'),
    path('users/subscriptions/',
         FollowListView.as_view(), name='follow_list'),
    path('users/<int:pk>/subscribe/',
         FollowUnfollowView.as_view(), name='follow_unfollow'),
    path('recipes/favorites/',
         FavoriteListView.as_view(), name='favorite_list'),
    path('recipes/<int:pk>/favorite/',
         FavoriteCreateDestroyView.as_view(), name='favorite'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
