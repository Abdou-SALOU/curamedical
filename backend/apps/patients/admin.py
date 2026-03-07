from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'date_of_birth',
                    'phone', 'blood_group', 'is_archived']
    list_filter = ['gender', 'blood_group', 'is_archived']
    search_fields = ['last_name', 'first_name', 'national_id']