from django.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
from django.utils import timezone

def restaurant_logo_path(instance, filename):
    # File will be uploaded to media/restaurant_logos/filename
    return f'restaurant_logos/{filename}'

def restaurant_cover_path(instance, filename):
    # File will be uploaded to media/restaurant_covers/filename
    return f'restaurant_covers/{filename}'

def restaurant_qr_path(instance, filename):
    # File will be uploaded to media/restaurant_qr_codes/filename
    return f'restaurant_qr_codes/{filename}'

def menu_item_path(instance, filename):
    # File will be uploaded to media/menu_items/filename
    return f'menu_items/{filename}'

def table_qr_path(instance, filename):
    # File will be uploaded to media/table_qr_codes/filename
    return f'table_qr_codes/{filename}'

class Subscription(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free Plan'),
        ('pro', 'Pro Plan'),
        ('enterprise', 'Enterprise Plan'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)  # Only for Enterprise plan
    
    def __str__(self):
        return f"{self.user.username} - {self.get_plan_display()}"
    
    def can_create_restaurant(self):
        if not self.is_active:
            return False
        
        current_count = Restaurant.objects.filter(owner=self.user).count()
        
        if self.plan == 'free' and current_count >= 1:
            return False
        elif self.plan == 'pro' and current_count >= 3:
            return False
        elif self.plan == 'enterprise':
            return True
            
        return True
    
    def can_customize_qr(self):
        return self.plan in ['pro', 'enterprise']
    
    def has_analytics(self):
        return self.plan in ['pro', 'enterprise']
    
    def has_priority_support(self):
        return self.plan in ['pro', 'enterprise']
    
    def has_24_7_support(self):
        return self.plan == 'enterprise'
    
    def has_custom_integration(self):
        return self.plan == 'enterprise'

class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    logo = models.ImageField(upload_to=restaurant_logo_path, null=True, blank=True, max_length=255)
    cover_image = models.ImageField(upload_to=restaurant_cover_path, null=True, blank=True, max_length=255)
    qr_code = models.ImageField(upload_to=restaurant_qr_path, blank=True, null=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Theme Settings
    primary_color = ColorField(format='hexa', default='#007bff')
    secondary_color = ColorField(format='hexa', default='#6c757d')
    background_color = ColorField(format='hexa', default='#ffffff')
    text_color = ColorField(format='hexa', default='#212529')
    accent_color = ColorField(format='hexa', default='#17a2b8')
    font_family = models.CharField(
        max_length=50,
        choices=[
            ('Roboto', 'Roboto'),
            ('Open Sans', 'Open Sans'),
            ('Lato', 'Lato'),
            ('Poppins', 'Poppins'),
            ('Montserrat', 'Montserrat'),
        ],
        default='Roboto'
    )
    menu_style = models.CharField(
        max_length=20,
        choices=[
            ('modern', 'Modern Grid'),
            ('classic', 'Classic List'),
            ('elegant', 'Elegant Cards'),
            ('minimal', 'Minimal'),
        ],
        default='modern'
    )
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Generate QR code for the menu
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            # Use request.build_absolute_uri in views instead of hardcoding the URL
            menu_url = f'/menu/{self.id}/'
            qr.add_data(menu_url)
            qr.make(fit=True)

            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to RGB if necessary
            if qr_image.mode != 'RGB':
                qr_image = qr_image.convert('RGB')
            
            # Save QR code
            qr_buffer = BytesIO()
            qr_image.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            self.qr_code.save(f'menu_qr_{self.id}.png',
                            File(qr_buffer), save=False)

        # Optimize logo if it exists and has changed
        if self.logo and hasattr(self.logo, 'file'):
            img = Image.open(self.logo)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Set a fixed size for logos
            output_size = (300, 300)
            img.thumbnail(output_size, Image.Resampling.LANCZOS)
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=85)
            img_io.seek(0)
            self.logo.save(self.logo.name.split('/')[-1], File(img_io), save=False)

        # Optimize cover image if it exists and has changed
        if self.cover_image and hasattr(self.cover_image, 'file'):
            cover = Image.open(self.cover_image)
            if cover.mode != 'RGB':
                cover = cover.convert('RGB')
            # Set a fixed aspect ratio for cover images (16:9)
            target_ratio = 16/9
            current_ratio = cover.width / cover.height
            
            if current_ratio > target_ratio:
                new_width = int(cover.height * target_ratio)
                left = (cover.width - new_width) // 2
                cover = cover.crop((left, 0, left + new_width, cover.height))
            else:
                new_height = int(cover.width / target_ratio)
                top = (cover.height - new_height) // 2
                cover = cover.crop((0, top, cover.width, top + new_height))
            
            # Resize to a reasonable max size while maintaining aspect ratio
            max_dimension = 1920
            cover.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            cover_io = BytesIO()
            cover.save(cover_io, format='PNG', quality=85)
            cover_io.seek(0)
            self.cover_image.save(self.cover_image.name.split('/')[-1], File(cover_io), save=False)

        super().save(*args, **kwargs)

class MenuCategory(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Menu Categories'
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to=menu_item_path, blank=True, null=True, max_length=255)
    is_available = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    # Dietary information
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')
    table_number = models.CharField(max_length=50)
    seats = models.IntegerField(default=2)
    qr_code = models.ImageField(upload_to=table_qr_path, blank=True)

    def __str__(self):
        return f"{self.restaurant.name} - Table {self.table_number}"

    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f'table/{self.id}')
            qr.make(fit=True)

            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to RGB if necessary
            if qr_image.mode != 'RGB':
                qr_image = qr_image.convert('RGB')
            
            # Save QR code
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            self.qr_code.save(f'qr_code_{self.restaurant.id}_{self.table_number}.png',
                            File(buffer), save=False)
        
        super().save(*args, **kwargs)
