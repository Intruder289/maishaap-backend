from django.contrib import admin
from .models import (
    Region, PropertyType, Amenity, Property, 
    PropertyAmenity, PropertyImage, PropertyView, PropertyFavorite
)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ['image', 'caption', 'is_primary', 'order']


class PropertyAmenityInline(admin.TabularInline):
    model = PropertyAmenity
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'property_type', 'region', 'bedrooms', 
        'bathrooms', 'rent_amount', 'status', 'owner', 'created_at'
    ]
    list_filter = [
        'status', 'property_type', 'region', 'bedrooms', 
        'bathrooms', 'is_featured', 'is_furnished', 'pets_allowed'
    ]
    search_fields = ['title', 'description', 'address', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PropertyImageInline, PropertyAmenityInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'property_type', 'status')
        }),
        ('Location', {
            'fields': ('region', 'address', 'latitude', 'longitude')
        }),
        ('Property Details', {
            'fields': (
                'bedrooms', 'bathrooms', 'size_sqft', 
                'floor_number', 'total_floors'
            )
        }),
        ('Pricing', {
            'fields': ('rent_amount', 'deposit_amount', 'utilities_included')
        }),
        ('Property Features', {
            'fields': (
                'is_featured', 'is_furnished', 'pets_allowed', 
                'smoking_allowed', 'available_from'
            )
        }),
        ('Management', {
            'fields': ('owner',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'caption', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['property__title', 'caption']


@admin.register(PropertyView)
class PropertyViewAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['property__title', 'user__username', 'ip_address']
    readonly_fields = ['viewed_at']


@admin.register(PropertyFavorite)
class PropertyFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'property__title']
