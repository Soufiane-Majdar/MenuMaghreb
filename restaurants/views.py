from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from .models import Restaurant, MenuCategory, MenuItem, Table, Subscription
from .forms import RestaurantForm, MenuCategoryForm, MenuItemForm, RestaurantThemeForm, CustomUserCreationForm
from django.core.mail import send_mail
from django.conf import settings
from .decorators import cache_page_for_restaurant, cache_menu_page
import logging

logger = logging.getLogger(__name__)

# Create your views here.

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'restaurants/landing.html')

@login_required
@cache_page_for_restaurant(timeout=300)
def dashboard(request):
    # Get or create subscription
    subscription, created = Subscription.objects.get_or_create(
        user=request.user,
        defaults={'plan': 'free', 'is_active': True}
    )
    
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
    logger.info("Starting restaurant creation process")
    subscription = get_object_or_404(Subscription, user=request.user)
    
    if not subscription.can_create_restaurant():
        logger.warning(f"User {request.user.username} exceeded restaurant limit for subscription plan {subscription.plan}")
        messages.error(request, 'You have reached the maximum number of restaurants for your subscription plan.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        logger.info(f"Processing POST request for restaurant creation by user {request.user.username}")
        form = RestaurantForm(request.POST, request.FILES)
        logger.info(f"Form data: {request.POST}")
        logger.info(f"Files: {request.FILES}")
        
        if form.is_valid():
            logger.info("Form is valid, proceeding with save")
            try:
                restaurant = form.save(commit=False)
                restaurant.owner = request.user
                
                # Set default values for required fields if not provided
                if not restaurant.primary_color:
                    restaurant.primary_color = '#007bff'
                if not restaurant.secondary_color:
                    restaurant.secondary_color = '#6c757d'
                if not restaurant.background_color:
                    restaurant.background_color = '#ffffff'
                if not restaurant.text_color:
                    restaurant.text_color = '#212529'
                if not restaurant.accent_color:
                    restaurant.accent_color = '#17a2b8'
                if not restaurant.font_family:
                    restaurant.font_family = 'Roboto'
                if not restaurant.menu_style:
                    restaurant.menu_style = 'modern'
                
                restaurant.save()
                logger.info(f"Successfully created restaurant: {restaurant.name}")
                messages.success(request, 'Restaurant created successfully!')
                return redirect('dashboard')
            except Exception as e:
                logger.error(f"Error saving restaurant: {str(e)}", exc_info=True)
                messages.error(request, f"Error creating restaurant: {str(e)}")
        else:
            logger.error(f"Form validation failed: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RestaurantForm()
        logger.info("Displaying empty restaurant creation form")
    
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
@cache_page_for_restaurant(timeout=300)
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

@cache_menu_page(timeout=3600)
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
        form = MenuItemForm(request.POST, request.FILES, restaurant=restaurant)
        if form.is_valid():
            item = form.save(commit=False)
            category = form.cleaned_data['category']
            item.category = category
            item.save()
            messages.success(request, 'Menu item created successfully!')
            return redirect('restaurant_menu_edit', restaurant_id=restaurant_id)
    else:
        form = MenuItemForm(restaurant=restaurant)
        
    # Get the category from query parameters if provided
    category_id = request.GET.get('category')
    if category_id:
        try:
            category = MenuCategory.objects.get(id=category_id, restaurant=restaurant)
            form.initial['category'] = category
        except MenuCategory.DoesNotExist:
            pass
            
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
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a free subscription for the new user
            Subscription.objects.create(
                user=user,
                plan='free',
                is_active=True
            )
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to MenuMaghreb.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'restaurants/register.html', {'form': form})

def contact_view(request):
    subject = request.GET.get('subject', '')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        plan = request.POST.get('plan')
        message = request.POST.get('message')
        
        # Prepare email content
        email_subject = f'New Contact Form Submission: {subject}'
        if plan:
            email_subject = f'New {plan.title()} Plan Inquiry'
            
        email_message = f"""
        New contact form submission from MenuMaghreb:
        
        Name: {name}
        Email: {email}
        Phone: {phone}
        Subject: {subject}
        Interested Plan: {plan.title() if plan else 'Not specified'}
        
        Message:
        {message}
        """
        
        # Send email notification with error logging
        try:
            print(f"Attempting to send email with settings:")
            print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
            print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
            print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
            print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
            
            # Send to admin
            send_mail(
                email_subject,
                email_message,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            
            # Send confirmation to user
            user_message = f"""
            Dear {name},
            
            Thank you for contacting MenuMaghreb! We have received your message and will get back to you shortly.
            
            Your message details:
            Subject: {subject}
            {f'Plan Interest: {plan.title()} Plan' if plan else ''}
            
            Best regards,
            MenuMaghreb Team
            """
            
            send_mail(
                'MenuMaghreb - Message Received',
                user_message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Your message has been sent successfully! We will contact you soon.')
            return redirect('contact')
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            messages.error(request, f'There was an error sending your message: {str(e)}')
            
    return render(request, 'restaurants/contact.html', {'subject': subject})

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
    current_subscription = None
    if request.user.is_authenticated:
        current_subscription = Subscription.objects.filter(user=request.user).first()
    
    plans = [
        {
            'name': 'Free Plan',
            'price': '0',
            'features': [
                'One Restaurant',
                'Basic Menu Management',
                'QR Code Generation',
                'Basic Support',
            ]
        },
        {
            'name': 'Pro Plan',
            'price': 'Contact Us',
            'features': [
                'Up to 3 Restaurants',
                'Advanced Menu Management',
                'Custom QR Codes',
                'Priority Support',
                'Analytics Dashboard',
                'Theme Customization',
            ]
        },
        {
            'name': 'Enterprise Plan',
            'price': 'Contact Us',
            'features': [
                'Unlimited Restaurants',
                'All Pro Features',
                '24/7 Priority Support',
                'Custom Integrations',
                'API Access',
                'Dedicated Account Manager',
            ]
        }
    ]
    
    context = {
        'plans': plans,
        'current_subscription': current_subscription
    }
    return render(request, 'restaurants/subscription_plans.html', context)

@login_required
def upgrade_subscription(request, plan):
    if plan not in ['pro', 'enterprise']:
        messages.error(request, 'Invalid subscription plan.')
        return redirect('subscription_plans')
    
    if not request.user.is_authenticated:
        messages.error(request, 'Please login to upgrade your subscription.')
        return redirect('login')
    
    # Prepare email subject and message
    plan_name = 'Pro Plan' if plan == 'pro' else 'Enterprise Plan'
    subject = f'New {plan_name} Subscription Request'
    
    # Get user details
    user = request.user
    current_subscription = Subscription.objects.filter(user=user).first()
    current_plan = current_subscription.plan if current_subscription else 'none'
    
    message = f"""
    New subscription upgrade request:
    
    User Details:
    - Username: {user.username}
    - Email: {user.email}
    - Current Plan: {current_plan}
    - Requested Plan: {plan_name}
    
    Restaurants:
    {Restaurant.objects.filter(owner=user).count()} restaurant(s)
    
    Please contact the user to process the upgrade.
    """
    
    # Send email to admin
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],  # Send to admin email
            fail_silently=False,
        )
        
        # Send confirmation email to user
        user_message = f"""
        Dear {user.username},
        
        Thank you for your interest in our {plan_name}!
        
        We have received your subscription upgrade request and our team will contact you shortly to process your upgrade and discuss payment options.
        
        Your current subscription will remain active until the upgrade is processed.
        
        Best regards,
        MenuMaghreb Team
        """
        
        send_mail(
            f'MenuMaghreb - {plan_name} Request Received',
            user_message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        messages.success(request, f'Thank you for your interest in our {plan_name}! We will contact you shortly to process your upgrade.')
    except Exception as e:
        messages.error(request, 'There was an error processing your request. Please try again later or contact support.')
    
    return redirect('dashboard')

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
