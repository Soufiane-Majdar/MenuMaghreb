from django import forms
from .models import Restaurant, MenuCategory, MenuItem
from colorfield.widgets import ColorWidget

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
    class Meta:
        model = Restaurant
        fields = [
            'name', 'description', 'address', 'phone',
            'logo', 'cover_image',
            'primary_color', 'secondary_color', 'background_color',
            'text_color', 'accent_color',
            'font_family', 'menu_style'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'primary_color': ColorWidget(),
            'secondary_color': ColorWidget(),
            'background_color': ColorWidget(),
            'text_color': ColorWidget(),
            'accent_color': ColorWidget(),
            'font_family': forms.Select(attrs={'class': 'form-select'}),
            'menu_style': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
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
            'logo': 'Upload a square logo image (recommended size: 200x200px)',
            'cover_image': 'Upload a wide cover image (recommended size: 1200x400px)',
            'primary_color': 'Main brand color used for headers and buttons',
            'secondary_color': 'Used for secondary elements',
            'background_color': 'Background color of the menu',
            'text_color': 'Color of the menu text',
            'accent_color': 'Used for highlighting and special elements',
            'font_family': 'Choose the font for your menu text',
            'menu_style': 'Select the overall layout of your menu'
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
        fields = ['category', 'name', 'description', 'price', 'image', 'is_available', 'order']
        widgets = {
            'price': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'order': forms.NumberInput(attrs={'min': 0}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if restaurant:
            self.fields['category'].queryset = MenuCategory.objects.filter(restaurant=restaurant)
        elif self.instance and self.instance.category:
            self.fields['category'].queryset = MenuCategory.objects.filter(restaurant=self.instance.category.restaurant)
