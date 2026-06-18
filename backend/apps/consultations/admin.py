from django.contrib import admin
from .models import Consultation


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = (
        'patient', 'medecin', 'diagnostic',
        'ia_utilisee', 'date_consultation'
    )
    list_filter = ('ia_utilisee', 'date_consultation', 'medecin')
    search_fields = (
        'patient__nom', 'patient__prenom',
        'symptomes', 'diagnostic'
    )
    readonly_fields = ('date_consultation', 'modifie_le', 'suggestions_ia')
    ordering = ('-date_consultation',)
    date_hierarchy = 'date_consultation'
    list_per_page = 25

    fieldsets = (
        ('Informations générales', {
            'fields': ('rendez_vous', 'patient', 'medecin', 'date_consultation')
        }),
        ('Contenu médical', {
            'fields': ('symptomes', 'examen_clinique', 'diagnostic', 'notes')
        }),
        ('Module IA', {
            'fields': ('ia_utilisee', 'suggestions_ia'),
            'classes': ('collapse',)
        }),
    )
