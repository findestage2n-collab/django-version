from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class HospitalUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Contact", {"fields": ("telephone",)}),)
    list_display = ("username", "first_name", "last_name", "is_active", "is_staff")
