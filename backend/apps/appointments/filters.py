import django_filters
from .models import RendezVous


class RendezVousFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(
        field_name='date_heure', lookup_expr='date',
        label="Date exacte"
    )
    date_min = django_filters.DateFilter(
        field_name='date_heure', lookup_expr='date__gte',
        label="Date minimum"
    )
    date_max = django_filters.DateFilter(
        field_name='date_heure', lookup_expr='date__lte',
        label="Date maximum"
    )
    medecin = django_filters.NumberFilter(field_name='medecin__id')
    patient = django_filters.NumberFilter(field_name='patient__id')
    statut = django_filters.ChoiceFilter(choices=RendezVous.CHOIX_STATUT)

    class Meta:
        model = RendezVous
        fields = ['statut', 'medecin', 'patient', 'date', 'date_min', 'date_max']
