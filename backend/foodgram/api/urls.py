from api.views import (UserViewSet, FollowView,
                       IngredientViewSet, RecipeViewSet,
                       TagViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

app_name = 'api'

router = DefaultRouter()

router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('users/subscriptions/',
         FollowView.as_view(), name='follow_list'),
    path('users/<int:pk>/subscribe/',
         FollowView.as_view(), name='follow_unfollow'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
