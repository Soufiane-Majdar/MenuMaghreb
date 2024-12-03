from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from .models import Restaurant, MenuCategory, MenuItem, Table, Subscription
from .forms import RestaurantForm, MenuCategoryForm, MenuItemForm, RestaurantThemeForm

# Create your views here.

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'restaurants/landing.html')

@login_required
def dashboard(request):
    subscription = get_object_or_404(Subscription, user=request.user)
    restaurants = Restaurant.objects.filter(owner=request.user)
    
    # Get stats for all restaurants
    restaurant_stats = []
    for restaurant in restaurants:
        stats = {
            'restaurant': restaurant,
            'categories': MenuCategory.objects.filter(restaurant=restaurant),
            'total_items': MenuItem.objects.filter(category__restaurant=restaurant).count(),
            'active_items': MenuItem.objects.filter(category__restaurant=restaurant, is_available=True).count(),
        }
        restaurant_stats.append(stats)

    context = {
        'restaurant_stats': restaurant_stats,
        'subscription': subscription,
        'can_create_restaurant': subscription.can_create_restaurant()
    }
    return render(request, 'restaurants/dashboard.html', context)

@login_required
def restaurant_create(request):
    subscription = get_object_or_404(Subscription, user=request.user)
    
    if not subscription.can_create_restaurant():
        messages.error(request, 'You have reached the maximum number of restaurants for your subscription plan.')
        return redirect('dashboard')
    
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
    
    context = {
        'form': form,
        'is_create': True,
        'subscription': subscription
    }
    return render(request, 'restaurants/restaurant_form.html', context)

@login_required
def restaurant_edit(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    subscription = get_object_or_404(Subscription, user=request.user)
    
    if restaurant.owner != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Restaurant updated successfully!')
            return redirect('dashboard')
    else:
        form = RestaurantForm(instance=restaurant)
    
    context = {
        'form': form,
        'is_create': False,
        'subscription': subscription
    }
    return render(request, 'restaurants/restaurant_form.html', context)

@login_required
def restaurant_detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    return render(request, 'restaurants/restaurant_detail.html', {'restaurant': restaurant})

@login_required
def restaurant_menu_edit(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if restaurant.owner != request.user:
        raise PermissionDenied("You don't have permission to edit this restaurant's menu.")
    
    categories = restaurant.categories.all().prefetch_related('items').order_by('order')
    
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
    
    context = {
        'restaurant': restaurant,
        'categories': categories,
        'category_form': category_form,
        'subscription': request.user.subscription
    }
    return render(request, 'restaurants/restaurant_menu_edit.html', context)

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
    return render(request, 'restaurants/category_form.html', {
        'form': form,
        'restaurant': restaurant,
        'action': 'Create'
    })

@login_required
def category_edit(request, restaurant_id, category_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    category = get_object_or_404(MenuCategory, id=category_id, restaurant=restaurant)
    if request.method == 'POST':
        form = MenuCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('restaurant_menu_edit', restaurant_id=restaurant_id)
    else:
        form = MenuCategoryForm(instance=category)
    return render(request, 'restaurants/category_form.html', {
        'form': form,
        'restaurant': restaurant,
        'category': category,
        'action': 'Edit'
    })

@login_required
def delete_category(request, restaurant_id, category_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    category = get_object_or_404(MenuCategory, id=category_id, restaurant=restaurant)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
    else:
        messages.error(request, 'Invalid request method!')
    return redirect('restaurant_menu_edit', restaurant_id=restaurant_id)

@login_required
def item_create(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.restaurant = restaurant
            item.save()
            messages.success(request, 'Menu item created successfully!')
            return redirect('restaurant_menu_edit', restaurant_id=restaurant_id)
    else:
        form = MenuItemForm()
    return render(request, 'restaurants/item_form.html', {
        'form': form,
        'restaurant': restaurant,
        'action': 'Create'
    })

@login_required
def item_edit(request, restaurant_id, item_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    item = get_object_or_404(MenuItem, id=item_id, category__restaurant=restaurant)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item, restaurant=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item updated successfully!')
            return redirect('restaurant_menu_edit', restaurant_id=restaurant_id)
    else:
        form = MenuItemForm(instance=item, restaurant=restaurant)
    
    context = {
        'form': form,
        'restaurant': restaurant,
        'item': item
    }
    return render(request, 'restaurants/item_form.html', context)

@login_required
def delete_item(request, restaurant_id, item_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    item = get_object_or_404(MenuItem, id=item_id, restaurant=restaurant)
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Menu item deleted successfully!')
    else:
        messages.error(request, 'Invalid request method!')
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

def handler403(request, exception):
    return render(request, 'errors/403.html', status=403)

def handler404(request, exception):
    return render(request, 'errors/404.html', status=404)

def handler500(request):
    return render(request, 'errors/500.html', status=500)

@login_required
def delete_restaurant(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    if request.method == 'POST':
        restaurant.delete()
        messages.success(request, 'Restaurant deleted successfully!')
    return redirect('dashboard')

@login_required
def subscription_plans(request):
    current_subscription = request.user.subscription
    context = {
        'current_plan': current_subscription.plan,
        'subscription': current_subscription,
    }
    return render(request, 'restaurants/subscription_plans.html', context)

@login_required
def upgrade_subscription(request, plan):
    if request.method == 'POST':
        if plan not in ['free', 'pro', 'enterprise']:
            messages.error(request, 'Invalid subscription plan.')
            return redirect('subscription_plans')
            
        subscription = request.user.subscription
        subscription.plan = plan
        subscription.save()
        
        if plan == 'free':
            message = 'Successfully switched to Free plan.'
        else:
            message = f'Successfully upgraded to {plan.title()} plan!'
        
        messages.success(request, message)
        return redirect('dashboard')
        
    return redirect('subscription_plans')

@login_required
def theme_customize(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner=request.user)
    
    if request.method == 'POST':
        form = RestaurantThemeForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Theme settings updated successfully!')
            return redirect('restaurant_menu_edit', restaurant_id=restaurant.id)
    else:
        form = RestaurantThemeForm(instance=restaurant)
    
    context = {
        'restaurant': restaurant,
        'form': form,
    }
    return render(request, 'restaurants/theme_customize.html', context)
