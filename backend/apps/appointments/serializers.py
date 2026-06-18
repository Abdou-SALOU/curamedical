from rest_framework import serializers
from datetime import timedelta
from .models import RendezVous
from apps.patients.serializers import PatientListSerializer
from apps.users.serializers import UserSerializer


class RendezVousSerializer(serializers.ModelSerializer):
    patient_detail = PatientListSerializer(source='patient', read_only=True)
    medecin_detail = UserSerializer(source='medecin', read_only=True)
    heure_fin = serializers.SerializerMethodField()

    class Meta:
        model = RendezVous
        fields = [
            'id',
            'patient', 'patient_detail',
            'medecin', 'medecin_detail',
            'date_heure', 'heure_fin', 'duree',
            'motif', 'statut', 'type_consultation', 'lien_visio',
            'cree_le', 'modifie_le',
        ]
        read_only_fields = ['id', 'cree_le', 'modifie_le']
        extra_kwargs = {
            'patient': {'required': False}
        }

    def get_heure_fin(self, obj):
        return obj.get_heure_fin()

    def validate(self, data):
        medecin = data.get('medecin', getattr(self.instance, 'medecin', None))
        date_heure = data.get('date_heure', getattr(self.instance, 'date_heure', None))
        duree = data.get('duree', getattr(self.instance, 'duree', 30))

        if medecin and date_heure:
            fin = date_heure + timedelta(minutes=duree)
            qs = RendezVous.objects.filter(
                medecin=medecin,
                statut__in=['PLANIFIE', 'CONFIRME', 'EN_COURS'],
                date_heure__lt=fin,
                date_heure__gte=date_heure - timedelta(minutes=duree),
            ).exclude(pk=self.instance.pk if self.instance else None)

            for rdv in qs:
                rdv_fin = rdv.get_heure_fin()
                if rdv_fin > date_heure:
                    raise serializers.ValidationError(
                        f"Conflit horaire : Dr. {medecin.last_name} a déjà "
                        f"un RDV de {rdv.date_heure.strftime('%H:%M')} "
                        f"à {rdv_fin.strftime('%H:%M')}."
                    )
        return data


class RendezVousListSerializer(serializers.ModelSerializer):
    patient_nom = serializers.SerializerMethodField()
    medecin_nom = serializers.SerializerMethodField()
    heure_fin = serializers.SerializerMethodField()
    patient_email = serializers.EmailField(source='patient.email', read_only=True)
    patient_tel = serializers.CharField(source='patient.telephone', read_only=True)
    patient_detail = PatientListSerializer(source='patient', read_only=True)

    class Meta:
        model = RendezVous
        fields = [
            'id', 'patient', 'patient_nom', 'patient_email', 'patient_tel',
            'patient_detail', 'medecin_nom',
            'date_heure', 'heure_fin', 'duree',
            'motif', 'statut', 'type_consultation', 'lien_visio'
        ]

    def get_patient_nom(self, obj):
        return obj.patient.nom_complet

    def get_medecin_nom(self, obj):
        return obj.medecin.get_full_name() or obj.medecin.username

    def get_heure_fin(self, obj):
        return obj.get_heure_fin()


class SerializerMiseAJourStatut(serializers.Serializer):
    statut = serializers.ChoiceField(choices=RendezVous.CHOIX_STATUT)
