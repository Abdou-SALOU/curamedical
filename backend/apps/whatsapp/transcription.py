import io
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# WhatsApp envoie les vocaux en ogg/opus ; d'autres formats sont possibles
_EXT_MAP = {
    'audio/ogg':  'ogg',
    'audio/mpeg': 'mp3',
    'audio/mp4':  'mp4',
    'audio/amr':  'amr',
    'audio/wav':  'wav',
}


def transcribe_whatsapp_audio(media_url: str, content_type: str = 'audio/ogg') -> str | None:
    """
    Télécharge le fichier audio depuis Twilio et le transcrit via Groq Whisper.
    Retourne le texte transcrit, ou None en cas d'échec.
    """
    if not settings.GROQ_API_KEY:
        logger.warning("[Whisper] GROQ_API_KEY non configuré — transcription désactivée.")
        return None

    try:
        # Twilio protège ses fichiers médias par HTTP Basic Auth
        response = requests.get(
            media_url,
            auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            timeout=30,
        )
        response.raise_for_status()
    except Exception as exc:
        logger.error("[Whisper] Téléchargement audio échoué : %s", exc)
        return None

    try:
        from groq import Groq

        ct = content_type.split(';')[0].strip()
        ext = _EXT_MAP.get(ct, 'ogg')

        audio_file = io.BytesIO(response.content)
        audio_file.name = f'whatsapp_voice.{ext}'

        client = Groq(api_key=settings.GROQ_API_KEY)
        result = client.audio.transcriptions.create(
            model='whisper-large-v3',
            file=audio_file,
            language='fr',          # détection automatique si la langue est autre
            response_format='text',
        )

        # Groq retourne une str directement quand response_format='text'
        text = result.strip() if isinstance(result, str) else getattr(result, 'text', '').strip()
        logger.info("[Whisper] Transcription : %.120s", text)
        return text or None

    except Exception as exc:
        logger.error("[Whisper] Erreur transcription Groq : %s", exc, exc_info=True)
        return None
