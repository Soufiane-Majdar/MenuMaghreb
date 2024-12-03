from django.contrib import admin
from django.utils.html import format_html
from .models import Restaurant, MenuCategory, MenuItem, Subscription

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'display_logo', 'display_qr_code', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'owner__username', 'description')
    readonly_fields = ('created_at', 'updated_at', 'display_qr_code')
    date_hierarchy = 'created_at'
    
    def display_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.logo.url)
        return "-"
    display_logo.short_description = 'Logo'

    def display_qr_code(self, obj):
        if obj.qr_code:
            download_url = obj.qr_code.url
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" width="100" height="100" style="margin-bottom: 5px;" /><br>'
                '<a href="{}" class="button" download style="padding: 5px 10px; '
                'background: #79aec8; color: white; text-decoration: none; '
                'border-radius: 4px;">Download QR Code</a>'
                '</div>',
                obj.qr_code.url, download_url
            )
        return "QR code not generated"
    display_qr_code.short_description = 'Menu QR Code'

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'owner', 'description', 'address', 'phone')
        }),
        ('Branding', {
            'fields': ('logo', 'cover_image', 'display_qr_code'),
            'classes': ('collapse',)
        }),
        ('Theme Settings', {
            'fields': (
                'primary_color', 'secondary_color', 'background_color',
                'text_color', 'accent_color', 'font_family', 'menu_style'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'order')
    list_filter = ('restaurant',)
    search_fields = ('name', 'restaurant__name')
    ordering = ('restaurant', 'order')

    fieldsets = (
        (None, {
            'fields': ('restaurant', 'name', 'order')
        }),
    )

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'display_image', 'is_available')
    list_filter = ('category__restaurant', 'category', 'is_available', 'is_vegetarian', 'is_vegan', 'is_gluten_free')
    search_fields = ('name', 'description', 'category__name', 'category__restaurant__name')
    ordering = ('category', 'order')

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 8px;" />', obj.image.url)
        return "-"
    display_image.short_description = 'Image'

    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'description', 'price')
        }),
        ('Image', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Dietary Information', {
            'fields': ('is_vegetarian', 'is_vegan', 'is_gluten_free'),
            'classes': ('collapse',)
        }),
        ('Display Options', {
            'fields': ('order', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_active', 'start_date', 'end_date')
    list_filter = ('plan', 'is_active')
    search_fields = ('user__username', 'plan')
    readonly_fields = ('start_date',)

    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'plan', 'is_active')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',)
        }),
    )
