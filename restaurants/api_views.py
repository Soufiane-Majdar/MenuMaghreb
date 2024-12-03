from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import MenuCategory, MenuItem, Restaurant
from .serializers import MenuCategorySerializer, MenuItemSerializer, RestaurantSerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Restaurant.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class MenuCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = MenuCategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MenuCategory.objects.filter(restaurant__owner=self.request.user)

    def perform_create(self, serializer):
        restaurant = get_object_or_404(Restaurant, id=self.request.data.get('restaurant'), owner=self.request.user)
        serializer.save(restaurant=restaurant)

    @action(detail=False, methods=['post'])
    def update_order(self, request):
        categories = request.data.get('categories', [])
        for cat_data in categories:
            category = get_object_or_404(MenuCategory, id=cat_data['id'], restaurant__owner=request.user)
            category.order = cat_data['order']
            category.save()
        return Response({'status': 'success'})

class MenuItemViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MenuItem.objects.filter(category__restaurant__owner=self.request.user)

    def perform_create(self, serializer):
        category = get_object_or_404(MenuCategory, id=self.request.data.get('category'), restaurant__owner=self.request.user)
        serializer.save(category=category)

    @action(detail=False, methods=['post'])
    def update_order(self, request):
        items = request.data.get('items', [])
        for item_data in items:
            item = get_object_or_404(MenuItem, id=item_data['id'], category__restaurant__owner=request.user)
            item.order = item_data['order']
            item.save()
        return Response({'status': 'success'})
