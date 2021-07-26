from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='organizations-home'),
    path('about/', views.about, name='organizations-about'),    
    path('favorites/', views.favorites, name='organizations-favorites'),
    path('results/', views.results, name='organizations-results'),
    path('search/', views.search, name='organizations-search'),
    path('organizations/<str:ein>/', views.organization, name='organizations-organization'),
    path('addFavorite/<str:ein>', views.newFavorite, name='organizations-newFavorite'),
    path('deleteFavorite/<str:ein>', views.deleteFavorite, name='organizations-deleteFavorite'),

]

