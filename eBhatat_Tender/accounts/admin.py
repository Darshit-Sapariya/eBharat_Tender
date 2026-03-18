from django.contrib import admin
from .models import UserProfile
from .models import AdminRequest

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'role', 'status')

    search_fields = ('user__username', 'full_name', 'mobile')

    readonly_fields = ('user', 'created_at')

    actions = ['approve_users', 'reject_users']

    def approve_users(self, request, queryset):
        queryset.update(status='approved')
    approve_users.short_description = "Approve selected users"

    def reject_users(self, request, queryset):
        queryset.update(status='rejected')
    reject_users.short_description = "Reject selected users"

@admin.register(AdminRequest)
class AdminRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'department_name', 'category_name', 'status')
    list_filter = ('status', 'department_name', 'category_name')
    search_fields = ('user__username', 'department_name', 'category_name')
    readonly_fields = ('created_at',)
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        queryset.update(status='approved')

    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
    
