from django.urls import path
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public pages
    path('', views.landing, name='landing'),
    path('contact/', views.contact_view, name='contact'),
    path('menu/<int:restaurant_id>/', views.menu_view, name='menu_view'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # Subscription
    path('subscription/plans/', login_required(views.subscription_plans), name='subscription_plans'),
    path('subscription/upgrade/<str:plan>/', login_required(views.upgrade_subscription), name='upgrade_subscription'),
    
    # Dashboard and restaurant management
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('restaurant/create/', login_required(views.restaurant_create), name='restaurant_create'),
    path('restaurant/<int:pk>/edit/', login_required(views.restaurant_edit), name='restaurant_edit'),
    path('restaurant/<int:restaurant_id>/delete/', login_required(views.delete_restaurant), name='delete_restaurant'),
    path('restaurant/<int:restaurant_id>/menu/edit/', login_required(views.restaurant_menu_edit), name='restaurant_menu_edit'),
    
    # Menu management
    path('restaurant/<int:restaurant_id>/category/create/', login_required(views.category_create), name='category_create'),
    path('restaurant/<int:restaurant_id>/category/<int:category_id>/edit/', login_required(views.category_edit), name='category_edit'),
    path('restaurant/<int:restaurant_id>/category/<int:category_id>/delete/', login_required(views.delete_category), name='delete_category'),
    
    # Theme customization
    path('restaurant/<int:restaurant_id>/theme/', login_required(views.theme_customize), name='theme_customize'),
    
    path('restaurant/<int:restaurant_id>/item/create/', login_required(views.item_create), name='item_create'),
    path('restaurant/<int:restaurant_id>/item/<int:item_id>/edit/', login_required(views.item_edit), name='item_edit'),
    path('restaurant/<int:restaurant_id>/item/<int:item_id>/delete/', login_required(views.delete_item), name='delete_item'),
]
