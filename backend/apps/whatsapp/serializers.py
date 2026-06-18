from rest_framework import serializers
from .models import WhatsAppConversation, WhatsAppMessage


class WhatsAppMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMessage
        fields = ('id', 'direction', 'body', 'media_url', 'twilio_sid', 'sent_at')


class WhatsAppConversationSerializer(serializers.ModelSerializer):
    messages = WhatsAppMessageSerializer(many=True, read_only=True)
    patient_nom = serializers.SerializerMethodField()

    class Meta:
        model = WhatsAppConversation
        fields = ('id', 'phone_number', 'patient', 'patient_nom', 'created_at', 'updated_at', 'messages')

    def get_patient_nom(self, obj):
        if obj.patient:
            return obj.patient.nom_complet
        return None


class WhatsAppConversationListSerializer(serializers.ModelSerializer):
    patient_nom = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = WhatsAppConversation
        fields = ('id', 'phone_number', 'patient', 'patient_nom', 'message_count', 'last_message', 'updated_at')

    def get_patient_nom(self, obj):
        return obj.patient.nom_complet if obj.patient else None

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-sent_at').first()
        return msg.body[:100] if msg else None
