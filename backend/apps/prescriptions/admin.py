from django.contrib import admin
from .models import Prescription, LignePrescription


class LignePrescriptionInline(admin.TabularInline):
    model = LignePrescription
    extra = 1
    fields = ('medicament', 'dosage', 'unite', 'frequence', 'duree', 'instructions')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        'patient', 'medecin',
        'nb_medicaments', 'cree_le'
    )
    list_filter = ('medecin', 'cree_le')
    search_fields = (
        'patient__nom', 'patient__prenom',
        'lignes__medicament'
    )
    readonly_fields = ('cree_le', 'modifie_le')
    ordering = ('-cree_le',)
    date_hierarchy = 'cree_le'
    list_per_page = 25
    inlines = [LignePrescriptionInline]

    def nb_medicaments(self, obj):
        return obj.lignes.count()
    nb_medicaments.short_description = "Nb médicaments"
