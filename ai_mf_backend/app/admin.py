from django.contrib import admin
from .models import UserLogs, UserManagement

@admin.register(UserLogs)
class UserLogsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_id', 'last_access', 'action')
    search_fields = ('email_id', 'name')
    list_filter = ('action', 'device_type')
    ordering = ('-last_access',)

@admin.register(UserManagement)
class UserManagementAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_verified')
    search_fields = ('email', 'name')
    list_filter = ('is_verified',)
    ordering = ('-created_at',)
