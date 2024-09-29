from django.contrib import admin
from ai_mf_backend.models.v1.database.user_authentication import (
    UserLogs,
    UserManagement,
)


@admin.register(UserLogs)
class UserLogsAdmin(admin.ModelAdmin):
    list_display = ("mobile_number", "email_id", "last_access", "action")
    search_fields = ("email_id", "mobile_number")
    list_filter = ("action", "device_type")
    ordering = ("-last_access",)


@admin.register(UserManagement)
class UserManagementAdmin(admin.ModelAdmin):
    list_display = ("mobile_number", "email", "created_at")
    search_fields = ("email", "mobile_number")
    list_filter = ("updated_at",)
    ordering = ("-created_at",)
