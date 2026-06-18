from django.contrib import admin
from .models import RendezVous


@admin.register(RendezVous)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medecin', 'date_heure', 'duree', 'statut', 'motif')
    list_filter = ('statut', 'date_heure', 'medecin')
    search_fields = ('patient__nom', 'patient__prenom', 'medecin__last_name', 'motif')
    ordering = ('-date_heure',)
    readonly_fields = ('cree_le', 'modifie_le')   # ← corrigé
    date_hierarchy = 'date_heure'
    list_per_page = 25
    actions = ['confirmer_rdv', 'annuler_rdv']

    def confirmer_rdv(self, request, queryset):
        queryset.update(statut='CONFIRME')
    confirmer_rdv.short_description = "Confirmer les RDV sélectionnés"

    def annuler_rdv(self, request, queryset):
        queryset.update(statut='ANNULE')
    annuler_rdv.short_description = "Annuler les RDV sélectionnés"
