from rest_framework import serializers
from .models import Prescription, PrescriptionItem

class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = '__all__'
        extra_kwargs = {
            'prescription': {'required': False},
            'instructions': {'required': False},
        }

class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True)
    patient_name = serializers.CharField(
        source='consultation.patient.full_name', read_only=True
    )
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = '__all__'
        extra_kwargs = {
            'notes': {'required': False},
        }

    def get_doctor_name(self, obj):
       return obj.consultation.doctor.username

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        prescription = Prescription.objects.create(**validated_data)
        for item_data in items_data:
            PrescriptionItem.objects.create(
                prescription=prescription, **item_data
            )
        return prescription