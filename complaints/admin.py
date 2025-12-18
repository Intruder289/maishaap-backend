from django.contrib import admin
from complaints.models import Complaint, ComplaintResponse, Feedback


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'title', 'user', 'property', 'category', 'priority', 
        'status', 'created_at', 'resolved_at'
    ]
    list_filter = ['status', 'category', 'priority', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status', 'priority']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'property', 'title', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'priority', 'status', 'rating')
        }),
        ('Resolution', {
            'fields': ('resolved_by', 'resolved_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'property', 'resolved_by')


@admin.register(ComplaintResponse)
class ComplaintResponseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'complaint', 'responder', 'response_type', 
        'is_visible_to_user', 'created_at'
    ]
    list_filter = ['response_type', 'is_visible_to_user', 'created_at']
    search_fields = ['complaint__title', 'responder__username', 'message']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('complaint', 'responder')


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'property', 'feedback_type', 'title', 
        'rating', 'created_at'
    ]
    list_filter = ['feedback_type', 'rating', 'created_at']
    search_fields = ['title', 'message', 'user__username', 'user__email']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'property', 'feedback_type', 'title', 'message')
        }),
        ('Rating', {
            'fields': ('rating',)
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'property')