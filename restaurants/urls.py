from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    # Landing and Dashboard
    path('', views.landing_page, name='landing'),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    
    # Restaurant Management
    path('restaurant/create/', login_required(views.restaurant_create), name='restaurant_create'),
    path('restaurant/<int:restaurant_id>/', login_required(views.restaurant_detail), name='restaurant_detail'),
    path('restaurant/<int:restaurant_id>/edit/', login_required(views.restaurant_edit), name='restaurant_edit'),
    path('restaurant/<int:restaurant_id>/menu/edit/', login_required(views.restaurant_menu_edit), name='restaurant_menu_edit'),
    
    # Menu Management
    path('restaurant/<int:restaurant_id>/menu/', views.menu_view, name='menu_view'),
    path('restaurant/<int:restaurant_id>/menu/edit/', login_required(views.menu_edit), name='menu_edit'),
    
    # Category Management
    path('restaurant/<int:restaurant_id>/category/create/', login_required(views.category_create), name='category_create'),
    path('category/<int:category_id>/edit/', login_required(views.category_edit), name='category_edit'),
    path('restaurant/<int:restaurant_id>/category/<int:category_id>/delete/', login_required(views.delete_category), name='delete_category'),
    
    # Item Management
    path('restaurant/<int:restaurant_id>/item/create/', login_required(views.item_create), name='item_create'),
    path('item/<int:item_id>/edit/', login_required(views.item_edit), name='item_edit'),
    path('restaurant/<int:restaurant_id>/item/<int:item_id>/delete/', login_required(views.delete_item), name='delete_item'),
    
    # Table Management
    path('restaurant/<int:restaurant_id>/tables/', login_required(views.table_management), name='table_management'),
    
    # Theme Settings
    path('restaurant/<int:restaurant_id>/theme/', login_required(views.theme_settings), name='theme_settings'),
    path('restaurant/<int:restaurant_id>/theme/', views.theme_customize, name='theme_customize'),
    
    # Contact
    path('contact/', views.contact_view, name='contact'),
    
    # Authentication
    path('register/', views.register, name='register'),
]
