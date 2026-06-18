from rest_framework import serializers
from .models import Prescription, LignePrescription
from apps.patients.serializers import PatientListSerializer
from apps.users.serializers import UserSerializer
from apps.common.tasks import dispatch_task
from .tasks import send_prescription_notification_task


class LignePrescriptionSerializer(serializers.ModelSerializer):
    unite_display = serializers.CharField(source='get_unite_display', read_only=True)

    class Meta:
        model = LignePrescription
        fields = (
            'id', 'medicament', 'dosage', 'unite', 'unite_display',
            'frequence', 'duree', 'instructions'
        )


class PrescriptionSerializer(serializers.ModelSerializer):
    lignes = LignePrescriptionSerializer(many=True)
    patient_detail = PatientListSerializer(source='patient', read_only=True)
    medecin_detail = UserSerializer(source='medecin', read_only=True)
    contenu = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = (
            'id',
            'consultation',
            'patient', 'patient_detail',
            'medecin', 'medecin_detail',
            'lignes', 'notes_generales',
            'contenu', 'cree_le', 'modifie_le'
        )
        read_only_fields = ('id', 'patient', 'patient_detail', 'medecin', 'medecin_detail', 'cree_le', 'modifie_le')

    def create(self, validated_data):
        lignes_data = validated_data.pop('lignes')
        prescription = Prescription.objects.create(**validated_data)
        for ligne in lignes_data:
            LignePrescription.objects.create(prescription=prescription, **ligne)

        # Email + PDF + n8n + WhatsApp en tâche de fond (Celery / thread de repli)
        dispatch_task(send_prescription_notification_task, prescription.id)
        return prescription

    def update(self, instance, validated_data):
        lignes_data = validated_data.pop('lignes', [])

        # Mise à jour des champs de la prescription
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Remplacement complet des lignes
        if lignes_data:
            instance.lignes.all().delete()
            for ligne in lignes_data:
                LignePrescription.objects.create(
                    prescription=instance,
                    **ligne
                )
        return instance

    def validate_consultation(self, value):
        """Une consultation ne peut avoir qu'une seule prescription."""
        qs = Prescription.objects.filter(consultation=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Cette consultation a déjà une ordonnance."
            )
        return value

    def get_contenu(self, obj):
        return "\n".join([f"- {l.medicament} {l.dosage}: {l.frequence} ({l.duree})" for l in obj.lignes.all()])


class PrescriptionListSerializer(serializers.ModelSerializer):
    """Serializer léger pour les listes."""
    patient_nom = serializers.SerializerMethodField()
    medecin_nom = serializers.SerializerMethodField()
    nb_medicaments = serializers.SerializerMethodField()
    contenu = serializers.SerializerMethodField()
    lignes = LignePrescriptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Prescription
        fields = (
            'id', 'patient_nom', 'medecin_nom',
            'nb_medicaments', 'lignes', 'notes_generales', 
            'contenu', 'cree_le'
        )

    def get_patient_nom(self, obj):
        return obj.patient.nom_complet

    def get_medecin_nom(self, obj):
        return obj.medecin.get_full_name() or obj.medecin.username

    def get_nb_medicaments(self, obj):
        # len() utilise le cache du prefetch_related — .count() relancerait une requête par ligne
        return len(obj.lignes.all())

    def get_contenu(self, obj):
        return "\n".join([f"- {l.medicament} {l.dosage}: {l.frequence} ({l.duree})" for l in obj.lignes.all()])
