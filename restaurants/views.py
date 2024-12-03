from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import Restaurant, MenuCategory, MenuItem, Table, MenuTheme
from .forms import RestaurantForm, MenuCategoryForm, MenuItemForm, RestaurantThemeForm

# Create your views here.

def landing_page(request):
    return render(request, 'restaurants/landing.html')

@login_required
def dashboard(request):
    restaurants = Restaurant.objects.filter(owner=request.user)
    return render(request, 'restaurants/dashboard.html', {'restaurants': restaurants})

@login_required
def restaurant_create(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            restaurant.save()
            messages.success(request, 'Restaurant created successfully!')
            return redirect('dashboard')
    else:
        form = RestaurantForm()
    return render(request, 'restaurants/restaurant_create.html', {'form': form})

@login_required
def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    return render(request, 'restaurants/restaurant_detail.html', {'restaurant': restaurant})

@login_required
def restaurant_edit(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Restaurant updated successfully!')
            return redirect('dashboard')
    else:
        form = RestaurantForm(instance=restaurant)
    return render(request, 'restaurants/restaurant_edit.html', {'form': form, 'restaurant': restaurant})

@login_required
def restaurant_menu_edit(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    categories = MenuCategory.objects.filter(restaurant=restaurant)
    
    if request.method == 'POST':
        category_form = MenuCategoryForm(request.POST)
        if category_form.is_valid():
            category = category_form.save(commit=False)
            category.restaurant = restaurant
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('restaurant_menu_edit', restaurant_id=restaurant_id)
    else:
        category_form = MenuCategoryForm()
    
    return render(request, 'restaurants/restaurant_menu_edit.html', {
        'restaurant': restaurant,
        'categories': categories,
        'category_form': category_form
    })

def menu_view(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    categories = MenuCategory.objects.filter(restaurant=restaurant).prefetch_related('items')
    table_number = request.GET.get('table', '')
    
    context = {
        'restaurant': restaurant,
        'categories': categories,
        'table_number': table_number,
    }
    return render(request, 'restaurants/menu.html', context)

@login_required
def menu_edit(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    categories = MenuCategory.objects.filter(restaurant=restaurant)
    
    if request.method == 'POST':
        item_form = MenuItemForm(request.POST, request.FILES)
        if item_form.is_valid():
            item = item_form.save(commit=False)
            category_id = request.POST.get('category')
            category = get_object_or_404(MenuCategory, id=category_id, restaurant=restaurant)
            item.category = category
            item.save()
            messages.success(request, 'Menu item added successfully!')
            return redirect('menu_edit', restaurant_id=restaurant_id)
    else:
        item_form = MenuItemForm()
    
    return render(request, 'restaurants/menu_edit.html', {
        'restaurant': restaurant,
        'categories': categories,
        'item_form': item_form
    })

@login_required
def category_create(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    if request.method == 'POST':
        form = MenuCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.restaurant = restaurant
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('restaurant_menu_edit', restaurant_id=restaurant_id)
    else:
        form = MenuCategoryForm()
    return render(request, 'restaurants/category_create.html', {'form': form, 'restaurant': restaurant})

@login_required
def category_edit(request, category_id):
    category = get_object_or_404(MenuCategory, id=category_id, restaurant__owner=request.user)
    
    if request.method == 'POST':
        form = MenuCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('restaurant_menu_edit', restaurant_id=category.restaurant.id)
    else:
        form = MenuCategoryForm(instance=category)
    
    return render(request, 'restaurants/category_edit.html', {
        'form': form,
        'category': category
    })

@login_required
def item_create(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, restaurant=restaurant)
        if form.is_valid():
            item = form.save(commit=False)
            item.category = form.cleaned_data['category']
            item.save()
            messages.success(request, 'Menu item created successfully!')
            return redirect('restaurant_menu_edit', restaurant_id=restaurant_id)
    else:
        form = MenuItemForm(restaurant=restaurant)
    
    return render(request, 'restaurants/item_create.html', {
        'form': form,
        'restaurant': restaurant,
    })

@login_required
def item_edit(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id, category__restaurant__owner=request.user)
    restaurant = item.category.restaurant
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item, restaurant=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item updated successfully!')
            return redirect('restaurant_menu_edit', restaurant_id=restaurant.id)
    else:
        form = MenuItemForm(instance=item, restaurant=restaurant)
    
    return render(request, 'restaurants/item_edit.html', {
        'form': form,
        'item': item,
        'restaurant': restaurant
    })

@login_required
def delete_category(request, restaurant_id, category_id):
    category = get_object_or_404(MenuCategory, id=category_id, restaurant__owner=request.user)
    
    if request.method == 'POST':
        restaurant_id = category.restaurant.id
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('restaurant_menu_edit', restaurant_id=restaurant_id)
    
    return redirect('restaurant_menu_edit', restaurant_id=restaurant_id)

@login_required
def delete_item(request, restaurant_id, item_id):
    item = get_object_or_404(MenuItem, id=item_id, category__restaurant__owner=request.user)
    item.delete()
    messages.success(request, 'Menu item deleted successfully!')
    return redirect('restaurant_menu_edit', restaurant_id=restaurant_id)

@login_required
def table_management(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    tables = Table.objects.filter(restaurant=restaurant)
    
    if request.method == 'POST':
        table_number = request.POST.get('table_number')
        seats = request.POST.get('seats', 2)
        
        table = Table.objects.create(
            restaurant=restaurant,
            table_number=table_number,
            seats=seats
        )
        messages.success(request, f'Table {table_number} created successfully!')
        return redirect('table_management', restaurant_id=restaurant_id)
    
    return render(request, 'restaurants/table_management.html', {
        'restaurant': restaurant,
        'tables': tables,
    })

@login_required
def theme_settings(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    theme, created = MenuTheme.objects.get_or_create(restaurant=restaurant)
    
    if request.method == 'POST':
        theme.primary_color = request.POST.get('primary_color', theme.primary_color)
        theme.secondary_color = request.POST.get('secondary_color', theme.secondary_color)
        theme.background_color = request.POST.get('background_color', theme.background_color)
        theme.font_family = request.POST.get('font_family', theme.font_family)
        theme.save()
        
        messages.success(request, 'Theme settings updated successfully!')
        return redirect('theme_settings', restaurant_id=restaurant_id)
    
    return render(request, 'restaurants/theme_settings.html', {
        'restaurant': restaurant,
        'theme': theme,
    })

@login_required
def theme_customize(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    
    if request.method == 'POST':
        form = RestaurantThemeForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Theme settings updated successfully!')
            return redirect('restaurant_menu_edit', restaurant_id=restaurant_id)
    else:
        form = RestaurantThemeForm(instance=restaurant)
    
    return render(request, 'restaurants/theme_customize.html', {
        'form': form,
        'restaurant': restaurant
    })

@login_required
def restaurant_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    restaurants = Restaurant.objects.filter(owner=request.user)
    return render(request, 'restaurants/restaurant_list.html', {'restaurants': restaurants})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def contact_view(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        plan = request.POST.get('plan')
        message = request.POST.get('message')
        
        # Here you would typically send an email to your sales team
        # For now, we'll just show a success message
        messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'restaurants/contact.html')
