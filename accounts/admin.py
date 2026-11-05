from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('SocioSolve Profile & Role', {
            'fields': (
                'role',
                'organization_name',
                'bio',
                'skills',
                'interests',
                'location',
                'avatar',
                'phone',
                'website',
            ),
        }),
    )
    list_display = ['username', 'email', 'role', 'organization_name', 'location', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'organization_name', 'skills']
