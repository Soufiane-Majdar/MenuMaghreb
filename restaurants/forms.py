from django import forms
from .models import Restaurant, MenuCategory, MenuItem

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'address', 'phone', 'logo', 'cover_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Restaurant Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Restaurant Description'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Restaurant Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

class RestaurantThemeForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = [
            'primary_color', 'secondary_color', 'background_color',
            'text_color', 'accent_color', 'font_family', 'menu_style'
        ]
        widgets = {
            'primary_color': forms.TextInput(attrs={'class': 'form-control color-picker'}),
            'secondary_color': forms.TextInput(attrs={'class': 'form-control color-picker'}),
            'background_color': forms.TextInput(attrs={'class': 'form-control color-picker'}),
            'text_color': forms.TextInput(attrs={'class': 'form-control color-picker'}),
            'accent_color': forms.TextInput(attrs={'class': 'form-control color-picker'}),
            'font_family': forms.Select(attrs={'class': 'form-control'}),
            'menu_style': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'primary_color': 'Primary Color',
            'secondary_color': 'Secondary Color',
            'background_color': 'Background Color',
            'text_color': 'Text Color',
            'accent_color': 'Accent Color',
            'font_family': 'Font Family',
            'menu_style': 'Menu Style',
        }

class MenuCategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'})
        }

class MenuItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        if restaurant:
            self.fields['category'].queryset = MenuCategory.objects.filter(restaurant=restaurant)
        
        # Update price field widget to show MAD
        self.fields['price'].widget.attrs.update({
            'step': '0.01',
            'min': '0',
            'placeholder': 'Price in MAD'
        })
        self.fields['price'].label = 'Price (MAD)'

    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'image', 'category', 'is_available', 'is_vegetarian', 'is_vegan', 'is_gluten_free']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Item Description'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_vegetarian': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_vegan': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_gluten_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
