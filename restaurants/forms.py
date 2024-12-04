from django import forms
from .models import Restaurant, MenuCategory, MenuItem
from colorfield.widgets import ColorWidget
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

FONT_CHOICES = [
    ('Arial', 'Arial'),
    ('Calibri', 'Calibri'),
    ('Courier New', 'Courier New'),
    ('Helvetica', 'Helvetica'),
    ('Times New Roman', 'Times New Roman'),
    ('Verdana', 'Verdana')
]

MENU_STYLE_CHOICES = [
    ('list', 'List'),
    ('grid', 'Grid')
]

class RestaurantForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make theme fields optional for free plan users
        theme_fields = ['primary_color', 'secondary_color', 'background_color', 
                       'text_color', 'accent_color', 'font_family', 'menu_style']
        for field in theme_fields:
            self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()
        # Set default values for any missing theme fields
        defaults = {
            'primary_color': '#2563EB',  # Modern blue
            'secondary_color': '#4B5563',  # Slate gray
            'background_color': '#F3F4F6',  # Light gray
            'text_color': '#1F2937',  # Dark gray
            'accent_color': '#10B981',  # Emerald green
            'font_family': 'Poppins',
            'menu_style': 'modern'
        }
        
        for field, default_value in defaults.items():
            if not cleaned_data.get(field):
                cleaned_data[field] = default_value
        
        return cleaned_data

    def save(self, commit=True):
        try:
            instance = super().save(commit=False)
            logger.info(f"Saving restaurant instance: {instance}")
            if commit:
                instance.save()
            return instance
        except Exception as e:
            logger.error(f"Error saving restaurant form: {str(e)}")
            raise

    class Meta:
        model = Restaurant
        fields = [
            'name', 'description', 'address', 'phone', 'email',
            'logo', 'cover_image',
            'primary_color', 'secondary_color', 'background_color',
            'text_color', 'accent_color',
            'font_family', 'menu_style'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 123-4567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'restaurant@example.com'}),
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'text_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'accent_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'font_family': forms.Select(attrs={'class': 'form-select'}),
            'menu_style': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'name': 'Restaurant Name',
            'description': 'Description',
            'address': 'Address',
            'phone': 'Phone Number',
            'email': 'Email (Optional)',
            'logo': 'Restaurant Logo',
            'cover_image': 'Cover Image',
            'primary_color': 'Primary Brand Color',
            'secondary_color': 'Secondary Brand Color',
            'background_color': 'Background Color',
            'text_color': 'Text Color',
            'accent_color': 'Accent Color',
            'font_family': 'Menu Font',
            'menu_style': 'Menu Layout Style'
        }
        help_texts = {
            'name': 'The name of your restaurant as it will appear on the menu',
            'description': 'A brief description of your restaurant',
            'logo': 'Your restaurant\'s logo (recommended size: 200x200px)',
            'cover_image': 'A cover image for your menu (recommended size: 1200x400px)',
            'primary_color': 'Main color for headers and buttons',
            'secondary_color': 'Color for secondary elements',
            'background_color': 'Menu background color',
            'text_color': 'Color for menu text',
            'accent_color': 'Color for highlights and special elements',
            'font_family': 'Choose a font that matches your brand',
            'menu_style': 'Select how your menu items will be displayed'
        }

class RestaurantThemeForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            'primary_color',
            'secondary_color',
            'background_color',
            'text_color',
            'accent_color',
            'font_family',
            'menu_style'
        ]
        widgets = {
            'primary_color': ColorWidget,
            'secondary_color': ColorWidget,
            'background_color': ColorWidget,
            'text_color': ColorWidget,
            'accent_color': ColorWidget,
            'font_family': forms.Select(choices=FONT_CHOICES),
            'menu_style': forms.Select(choices=MENU_STYLE_CHOICES),
        }

class MenuCategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = ['name', 'order']
        widgets = {
            'order': forms.NumberInput(attrs={'min': 0})
        }

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['category', 'name', 'description', 'price', 'image', 'is_available', 'order', 'is_vegetarian', 'is_vegan', 'is_gluten_free']
        widgets = {
            'price': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'order': forms.NumberInput(attrs={'min': 0}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_vegetarian': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_vegan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_gluten_free': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.restaurant = restaurant
        if restaurant:
            self.fields['category'].queryset = MenuCategory.objects.filter(restaurant=restaurant)
        elif self.instance and self.instance.category:
            self.fields['category'].queryset = MenuCategory.objects.filter(restaurant=self.instance.category.restaurant)
        
        # Make fields required and add help text
        self.fields['name'].required = True
        self.fields['price'].required = True
        self.fields['category'].required = True
        self.fields['description'].required = False
        
        # Add help text
        self.fields['price'].help_text = 'Enter the price in your local currency'
        self.fields['image'].help_text = 'Upload an image of the menu item (optional)'
        self.fields['order'].help_text = 'Order in which this item appears (lower numbers appear first)'

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if category and self.restaurant and category.restaurant != self.restaurant:
            raise forms.ValidationError("This category doesn't belong to the selected restaurant.")
        return category

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
