from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'scheduled_at', 'status', 'reason']
    list_filter = ['status', 'doctor']
    search_fields = ['patient__last_name', 'patient__first_name']