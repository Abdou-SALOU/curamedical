import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets, permissions, filters

from .models import WhatsAppConversation, WhatsAppMessage
from .serializers import WhatsAppConversationSerializer, WhatsAppConversationListSerializer

logger = logging.getLogger(__name__)


# ── Webhook Twilio ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_POST
def whatsapp_inbound(request):
    """
    Webhook Twilio — reçoit les messages WhatsApp entrants.
    POST /api/whatsapp/inbound/  (pas d'auth JWT, Twilio appelle directement)
    """
    if getattr(settings, 'TWILIO_VALIDATE_SIGNATURE', False):
        _validate_signature(request)

    from_raw          = request.POST.get('From', '')
    phone_number      = from_raw.replace('whatsapp:', '').strip()
    body              = request.POST.get('Body', '').strip()
    inbound_media_url = request.POST.get('MediaUrl0', '') or None
    media_content_type = request.POST.get('MediaContentType0', '')

    if not phone_number:
        return HttpResponse(status=400)

    conversation = _get_or_create_conversation(phone_number)

    # ── Transcription vocale (Whisper via Groq) ───────────────────────────────
    transcript = None
    if not body and inbound_media_url and media_content_type.startswith('audio/'):
        from .transcription import transcribe_whatsapp_audio
        transcript = transcribe_whatsapp_audio(inbound_media_url, media_content_type)

    effective_body = body or transcript

    # Sauvegarder le message entrant
    WhatsAppMessage.objects.create(
        conversation=conversation,
        direction=WhatsAppMessage.INBOUND,
        body=f"🎤 {transcript}" if transcript else (body or '(média)'),
        media_url=inbound_media_url,
    )

    # Générer la réponse via le chatbot
    if effective_body:
        reply_text, outbound_media_url = _process_message(conversation, effective_body)
        if transcript:
            reply_text = f"_(🎤 compris : « {transcript[:80]}{'…' if len(transcript)>80 else ''} »)_\n\n{reply_text}"
    else:
        reply_text, outbound_media_url = _welcome(), None

    # Sauvegarder la réponse sortante
    WhatsAppMessage.objects.create(
        conversation=conversation,
        direction=WhatsAppMessage.OUTBOUND,
        body=reply_text,
    )

    # Répondre à Twilio via TwiML
    from twilio.twiml.messaging_response import MessagingResponse
    twiml = MessagingResponse()
    msg = twiml.message(reply_text)
    if outbound_media_url:
        msg.media(outbound_media_url)
    return HttpResponse(str(twiml), content_type='text/xml')


def _process_message(conversation: WhatsAppConversation, message: str):
    from .chatbot import WhatsAppChatbot
    try:
        bot = WhatsAppChatbot(conversation)
        text = bot.process(message)
        return text, bot.media_url
    except Exception as e:
        logger.error("[WhatsApp] Chatbot error: %s", e, exc_info=True)
        return _welcome(), None


def _welcome() -> str:
    return (
        "👋 Bonjour ! Je suis l'assistant médical de *CuraMedical*.\n\n"
        "Tapez *menu* pour voir tout ce que je peux faire pour vous.\n"
        "🚨 Urgence : appelez le *15* (SAMU)."
    )


def _validate_signature(request):
    from twilio.request_validator import RequestValidator
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    url = request.build_absolute_uri()
    sig = request.META.get('HTTP_X_TWILIO_SIGNATURE', '')
    if not validator.validate(url, request.POST, sig):
        raise PermissionError('Signature Twilio invalide')


def _get_or_create_conversation(phone_number: str) -> WhatsAppConversation:
    conversation, _ = WhatsAppConversation.objects.get_or_create(phone_number=phone_number)
    if not conversation.patient:
        try:
            from apps.patients.models import Patient
            patient = Patient.objects.filter(telephone=phone_number).first()
            if patient:
                conversation.patient = patient
                conversation.save(update_fields=['patient'])
        except Exception:
            pass
    return conversation


# ── Historique des conversations ───────────────────────────────────────────────

class WhatsAppConversationViewSet(viewsets.ReadOnlyModelViewSet):
    """Historique des conversations WhatsApp — lecture seule, staff uniquement."""
    queryset = WhatsAppConversation.objects.prefetch_related('messages').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['phone_number', 'patient__nom', 'patient__prenom']
    ordering_fields = ['updated_at', 'created_at']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return WhatsAppConversationListSerializer
        return WhatsAppConversationSerializer

    def get_permissions(self):
        from apps.users.permissions import EstStaffOuAdministrateur
        return [permissions.IsAuthenticated(), EstStaffOuAdministrateur()]
