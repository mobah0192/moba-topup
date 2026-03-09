# apps/games/urls.py
from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    # Game URLs
    path('', views.game_list, name='list'),
    path('search/', views.search_games, name='search'),
    path('garena/', views.garena_store, name='garena'),
    
    # Article URLs
    path('articles/', views.article_list, name='article_list'),
    path('articles/category/<slug:slug>/', views.article_by_category, name='article_by_category'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    
    # API URLs
    path('api/items/<int:game_id>/', views.get_game_items_api, name='api_game_items'),
    path('api/validate-game-id/', views.check_game_id_api, name='api_validate_game_id'),
    path('<slug:slug>/', views.game_detail, name='detail'),
]