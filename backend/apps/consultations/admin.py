from django.contrib import admin
from .models import Consultation

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'diagnosis', 'ia_used', 'created_at']
    list_filter = ['ia_used', 'doctor']
    search_fields = ['appointment__patient__last_name', 'diagnosis']



