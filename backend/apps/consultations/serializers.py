from rest_framework import serializers
from .models import Consultation
from apps.patients.serializers import PatientListSerializer
from apps.users.serializers import UserSerializer


class SuggestionIASerializer(serializers.Serializer):
    """Structure d'une suggestion retournée par le microservice Flask."""
    pathologie = serializers.CharField()
    score = serializers.FloatField(min_value=0, max_value=100)
    description = serializers.CharField(required=False)


class ConsultationSerializer(serializers.ModelSerializer):
    patient_detail = PatientListSerializer(source='patient', read_only=True)
    medecin_detail = UserSerializer(source='medecin', read_only=True)

    class Meta:
        model = Consultation
        fields = (
            'id',
            'rendez_vous',
            'patient', 'patient_detail',
            'medecin', 'medecin_detail',
            'symptomes', 'examen_clinique',
            'diagnostic', 'notes',
            'suggestions_ia', 'ia_utilisee',
            'date_consultation', 'modifie_le',
        )
        read_only_fields = ('id', 'medecin', 'medecin_detail', 'date_consultation', 'modifie_le')
        extra_kwargs = {'patient': {'required': False}}

    def validate_rendez_vous(self, value):
        """Un RDV ne peut avoir qu'une seule consultation."""
        if value:
            qs = Consultation.objects.filter(rendez_vous=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "Ce rendez-vous a déjà une consultation associée."
                )
        return value


class ConsultationListSerializer(serializers.ModelSerializer):
    """Serializer léger pour les listes."""
    patient_nom = serializers.SerializerMethodField()
    medecin_nom = serializers.SerializerMethodField()

    class Meta:
        model = Consultation
        fields = (
            'id', 'patient', 'patient_nom', 'medecin_nom',
            'diagnostic', 'ia_utilisee',
            'date_consultation', 'rendez_vous'
        )

    def get_patient_nom(self, obj):
        return obj.patient.nom_complet

    def get_medecin_nom(self, obj):
        return obj.medecin.get_full_name() or obj.medecin.username
