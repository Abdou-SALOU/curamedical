from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'prenom', 'date_naissance',
        'age', 'telephone', 'groupe_sanguin',
        'est_archive'
    )
    list_filter = ('groupe_sanguin', 'sexe', 'est_archive', 'ville')
    search_fields = ('nom', 'prenom', 'cin', 'telephone', 'email')
    ordering = ('nom', 'prenom')
    readonly_fields = ('cree_le', 'modifie_le', 'age')
    list_per_page = 25
    date_hierarchy = 'cree_le'

    fieldsets = (
        ('Identité', {
            'fields': (
                'utilisateur', 'nom', 'prenom',
                'date_naissance', 'age', 'sexe', 'cin'
            )
        }),
        ('Coordonnées', {
            'fields': ('telephone', 'email', 'adresse', 'ville')
        }),
        ('Informations Médicales', {
            'fields': (
                'groupe_sanguin', 'allergies',
                'antecedents_medicaux', 'medicaments_en_cours'
            )
        }),
        ('Métadonnées', {
            'fields': ('est_archive', 'cree_le', 'modifie_le'),
            'classes': ('collapse',)
        }),
    )

    actions = ['archiver_patients']

    def archiver_patients(self, request, queryset):
        queryset.update(est_archive=True)
    archiver_patients.short_description = "Archiver les patients sélectionnés"
