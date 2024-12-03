from django.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
from django.utils import timezone

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
    logo = models.ImageField(upload_to='restaurant_logos/', null=True, blank=True)
    cover_image = models.ImageField(upload_to='restaurant_covers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Theme Settings
    primary_color = ColorField(default='#007bff')
    secondary_color = ColorField(default='#6c757d')
    background_color = ColorField(default='#ffffff')
    text_color = ColorField(default='#212529')
    accent_color = ColorField(default='#17a2b8')
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
        # Optimize logo if it exists
        if self.logo:
            img = Image.open(self.logo)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Set a fixed size for logos
            output_size = (300, 300)
            img.thumbnail(output_size, Image.Resampling.LANCZOS)
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=85)
            self.logo = File(img_io, name=self.logo.name)

        # Optimize cover image if it exists
        if self.cover_image:
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
            
            # Resize to a standard size
            cover.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
            cover_io = BytesIO()
            cover.save(cover_io, format='JPEG', quality=85)
            self.cover_image = File(cover_io, name=self.cover_image.name)

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
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
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
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    
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
            # Generate URL for this table's menu
            url = f'/menu/{self.restaurant.id}/?table={self.table_number}'
            qr.add_data(url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save QR code image
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            filename = f'qr_restaurant_{self.restaurant.id}_table_{self.table_number}.png'
            self.qr_code.save(filename, File(buffer), save=False)
        
        super().save(*args, **kwargs)

class MenuTheme(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='theme')
    primary_color = ColorField(default='#FF0000')
    secondary_color = ColorField(default='#00FF00')
    background_color = ColorField(default='#FFFFFF')
    font_family = models.CharField(max_length=100, default='Arial')
    
    def __str__(self):
        return f"{self.restaurant.name}'s Theme"
