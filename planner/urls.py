from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Профиль
    path('profile/', views.user_profile, name='user_profile'),
    
    # Контент
    path('plans/', views.content_plan_list, name='content_plan_list'),
    path('plans/create/', views.content_plan_create, name='content_plan_create'),
    path('plans/<int:pk>/', views.content_plan_detail, name='content_plan_detail'),
    path('plans/<int:pk>/edit/', views.content_plan_edit, name='content_plan_edit'),
    path('plans/<int:pk>/delete/', views.content_plan_delete, name='content_plan_delete'),
    
    # Элементы контента
    path('plans/<int:plan_pk>/items/create/', views.content_item_create, name='content_item_create'),
    path('items/<int:pk>/edit/', views.content_item_edit, name='content_item_edit'),
    path('items/<int:pk>/delete/', views.content_item_delete, name='content_item_delete'),
    
    # Календарь
    path('calendar/', views.content_calendar, name='content_calendar'),
    
    # Категории
    path('categories/', views.categories_list, name='categories_list'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
