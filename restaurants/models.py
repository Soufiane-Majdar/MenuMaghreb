from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
import cloudinary.uploader
import logging

logger = logging.getLogger(__name__)

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
    email = models.EmailField(blank=True, null=True)
    logo = CloudinaryField('logo', folder='restaurant_logos', blank=True, null=True)
    cover_image = CloudinaryField('cover_image', folder='restaurant_covers', blank=True, null=True)
    qr_code = CloudinaryField('qr_code', folder='restaurant_qr_codes', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Theme Colors - Modern defaults
    primary_color = models.CharField(
        max_length=7,
        default='#2563EB',  # Modern blue
        help_text='Main brand color, used for headers and primary buttons'
    )
    secondary_color = models.CharField(
        max_length=7,
        default='#4B5563',  # Slate gray
        help_text='Secondary color for accents and secondary buttons'
    )
    background_color = models.CharField(
        max_length=7,
        default='#F3F4F6',  # Light gray
        help_text='Background color of the menu'
    )
    text_color = models.CharField(
        max_length=7,
        default='#1F2937',  # Dark gray
        help_text='Main text color'
    )
    accent_color = models.CharField(
        max_length=7,
        default='#10B981',  # Emerald green
        help_text='Used for highlights and call-to-action elements'
    )
    
    # Typography and Layout
    font_family = models.CharField(
        max_length=50,
        choices=[
            ('Poppins', 'Poppins'),  # Modern, clean font
            ('Montserrat', 'Montserrat'),  # Professional, modern
            ('Open Sans', 'Open Sans'),  # Highly readable
            ('Roboto', 'Roboto'),  # Clean and modern
            ('Lato', 'Lato'),  # Friendly and natural
        ],
        default='Poppins',
        help_text='Main font family for the menu'
    )
    
    menu_style = models.CharField(
        max_length=20,
        choices=[
            ('modern', 'Modern Grid'),  # Default, modern card-based layout
            ('elegant', 'Elegant Cards'),  # Sophisticated layout with more whitespace
            ('classic', 'Classic List'),  # Traditional list view
            ('minimal', 'Minimal'),  # Clean, minimalist design
        ],
        default='modern',
        help_text='Overall layout style of the menu'
    )
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        if is_new or not self.qr_code:
            try:
                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                menu_url = f"https://your-domain.com/menu/{self.id}/"  # Replace with your actual domain
                qr.add_data(menu_url)
                qr.make(fit=True)

                # Create QR code image
                qr_image = qr.make_image(fill_color="black", back_color="white")
                
                # Convert to RGB if necessary
                if qr_image.mode != 'RGB':
                    qr_image = qr_image.convert('RGB')
                
                # Save to BytesIO
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                buffer.seek(0)

                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    buffer,
                    folder='restaurant_qr_codes',
                    public_id=f'qr_code_{self.id}',
                    overwrite=True
                )

                # Update the qr_code field without triggering another save
                self.qr_code = upload_result['url']
                type(self).objects.filter(pk=self.pk).update(qr_code=upload_result['url'])
                
            except Exception as e:
                logger.error(f"Error generating QR code for restaurant {self.id}: {str(e)}")

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
    image = CloudinaryField('image', folder='menu_items', blank=True, null=True)
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
    qr_code = CloudinaryField('qr_code', folder='table_qr_codes', blank=True)

    def save(self, *args, **kwargs):
        # First save to ensure we have an ID
        super().save(*args, **kwargs)
        
        # Generate QR code if it doesn't exist
        if not self.qr_code:
            # Get the absolute URL for the table's menu
            menu_url = f"http://127.0.0.1:8000{reverse('menu_view', args=[self.restaurant.id])}?table={self.table_number}"
            
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(menu_url)
            qr.make(fit=True)
            
            # Create image from QR code
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code to BytesIO
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Upload to Cloudinary
            cloudinary_response = cloudinary.uploader.upload(
                buffer,
                folder='table_qr_codes',
                public_id=f'table_qr_code_{self.restaurant.id}_{self.table_number}',
                overwrite=True
            )
            
            # Update the qr_code field with the Cloudinary URL
            self.qr_code = cloudinary_response['secure_url']
            
            # Save again to update the QR code field
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.restaurant.name} - Table {self.table_number}"
