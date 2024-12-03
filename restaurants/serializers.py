from rest_framework import serializers
from .models import Restaurant, MenuCategory, MenuItem

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'description', 'address', 'phone', 'logo', 'cover_image', 'created_at', 'updated_at']
        read_only_fields = ['owner']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'image', 'is_available', 'is_vegetarian', 'is_vegan', 'is_gluten_free', 'category']

class MenuCategorySerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'description', 'restaurant', 'items']
