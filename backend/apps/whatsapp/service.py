import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Wrapper Twilio pour l'envoi de messages WhatsApp."""

    def __init__(self):
        from twilio.rest import Client
        self._client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        from_raw = settings.TWILIO_WHATSAPP_FROM.strip()
        self._from = from_raw if from_raw.startswith('whatsapp:') else f"whatsapp:{from_raw}"

    def _normalize_number(self, number: str) -> str:
        number = number.strip()
        if not number.startswith('whatsapp:'):
            number = f"whatsapp:{number}"
        return number

    def send_message(self, to: str, body: str, media_url: str | None = None) -> object:
        """Envoie un message texte (et optionnellement un média) sur WhatsApp."""
        kwargs = {
            'from_': self._from,
            'to': self._normalize_number(to),
            'body': body,
        }
        if media_url:
            kwargs['media_url'] = [media_url]
        msg = self._client.messages.create(**kwargs)
        logger.info("WhatsApp envoyé à %s — SID %s", to, msg.sid)
        return msg

    def send_pdf(self, to: str, pdf_url: str, caption: str = '') -> object:
        """Envoie un PDF via WhatsApp avec un message d'accompagnement."""
        return self.send_message(to, caption or 'Votre document est disponible.', media_url=pdf_url)
