from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email',
        'first_name', 'last_name',
        'role', 'specialite', 'telephone',
        'is_staff', 'is_active'
    )
    list_filter = ('role', 'specialite', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('last_name', 'first_name')
    list_per_page = 25

    fieldsets = UserAdmin.fieldsets + (
        ('Informations Cabinet', {
            'fields': ('role', 'specialite', 'telephone')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations Cabinet', {
            'fields': ('role', 'specialite', 'telephone')
        }),
    )
