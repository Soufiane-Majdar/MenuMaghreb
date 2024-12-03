from django.contrib import admin
from .models import Restaurant, MenuCategory, MenuItem, Table

# Register your models here.

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'phone', 'created_at')
    search_fields = ('name', 'owner__username', 'phone')
    list_filter = ('created_at',)

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'order')
    list_filter = ('restaurant',)
    search_fields = ('name', 'restaurant__name')
    ordering = ('restaurant', 'order')

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_available')
    list_filter = ('category__restaurant', 'category', 'is_available')
    search_fields = ('name', 'description')
    ordering = ('category', 'order')

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'table_number', 'seats')
    list_filter = ('restaurant',)
    search_fields = ('table_number', 'restaurant__name')
