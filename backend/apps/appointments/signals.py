import logging
from zoneinfo import ZoneInfo

from celery import shared_task
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from apps.common.tasks import dispatch_task
from .models import RendezVous

logger = logging.getLogger(__name__)

TZ_CASA = ZoneInfo('Africa/Casablanca')

STATUTS_NOTIFICATION = {'CONFIRME', 'PLANIFIE'}

_JOURS_FR   = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
_MOIS_FR    = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
               'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']


def _format_date_fr(dt) -> str:
    local = dt.astimezone(TZ_CASA)
    return f"{_JOURS_FR[local.weekday()]} {local.day} {_MOIS_FR[local.month - 1]} {local.year}"


@receiver(pre_save, sender=RendezVous)
def capture_ancien_statut(sender, instance, **kwargs):
    """Capture le statut avant sauvegarde pour détecter les vrais changements."""
    if instance.pk:
        try:
            instance._ancien_statut = RendezVous.objects.get(pk=instance.pk).statut
        except RendezVous.DoesNotExist:
            instance._ancien_statut = None
    else:
        instance._ancien_statut = None


@receiver(post_save, sender=RendezVous)
def notifier_patient_confirmation(sender, instance, created, **kwargs):
    """
    Quand un RDV passe à CONFIRME ou PLANIFIE, envoie simultanément :
      - Un email HTML au patient
      - Un message WhatsApp via Twilio
    L'envoi est délégué à un worker Celery pour ne pas bloquer la requête
    HTTP (SMTP + Twilio peuvent prendre plusieurs secondes).
    """
    ancien_statut = getattr(instance, '_ancien_statut', None)
    nouveau_statut = instance.statut

    if nouveau_statut not in STATUTS_NOTIFICATION or ancien_statut == nouveau_statut:
        return

    if not instance.patient_id:
        return

    dispatch_task(notifier_rdv_task, instance.pk, nouveau_statut)


@shared_task(name='appointments.notifier_rdv')
def notifier_rdv_task(rdv_pk, nouveau_statut):
    try:
        instance = RendezVous.objects.select_related('patient', 'medecin').get(pk=rdv_pk)
    except RendezVous.DoesNotExist:
        return

    patient = instance.patient

    # ── Heure en heure locale Casablanca ──────────────────────────────────────
    date_heure_local = instance.date_heure.astimezone(TZ_CASA)
    date_str  = _format_date_fr(instance.date_heure)
    heure_str = date_heure_local.strftime('%H:%M')

    # ── Données communes ───────────────────────────────────────────────────────
    patient_nom  = patient.nom_complet
    medecin_nom  = instance.medecin.get_full_name() or f"Dr. {instance.medecin.last_name}"
    type_rdv     = instance.type_consultation
    is_visio     = type_rdv == 'EN_LIGNE'
    jitsi_url    = f"https://meet.jit.si/{instance.lien_visio}" if is_visio and instance.lien_visio else None
    base_url     = getattr(settings, 'PUBLIC_BASE_URL', '').rstrip('/')

    # ── Email ──────────────────────────────────────────────────────────────────
    if patient.email:
        _envoyer_email(
            patient=patient,
            patient_nom=patient_nom,
            medecin_nom=medecin_nom,
            date_str=date_str,
            heure_str=heure_str,
            motif=instance.motif or '',
            statut_display=instance.get_statut_display(),
            is_visio=is_visio,
            jitsi_url=jitsi_url,
            base_url=base_url,
            rdv=instance,
        )

    # ── WhatsApp ───────────────────────────────────────────────────────────────
    if patient.telephone:
        _envoyer_whatsapp(
            telephone=patient.telephone,
            patient_nom=patient_nom,
            medecin_nom=medecin_nom,
            date_str=date_str,
            heure_str=heure_str,
            motif=instance.motif or '',
            is_visio=is_visio,
            jitsi_url=jitsi_url,
            nouveau_statut=nouveau_statut,
        )


def _envoyer_email(*, patient, patient_nom, medecin_nom, date_str, heure_str,
                   motif, statut_display, is_visio, jitsi_url, base_url, rdv):
    # Lien vers l'espace patient = FRONTEND (et non PUBLIC_BASE_URL qui pointe
    # sur le backend ngrok et n'a pas de route /login).
    frontend_url = getattr(settings, 'FRONTEND_URL', '').rstrip('/')
    context = {
        'patient_nom':  patient_nom,
        'medecin_nom':  medecin_nom,
        'date_rdv':     date_str,
        'heure_rdv':    heure_str,
        'statut':       statut_display,
        'motif':        motif,
        'is_visio':     is_visio,
        'jitsi_url':    jitsi_url,
        'portal_url':   f"{frontend_url}/login" if frontend_url else None,
    }
    try:
        html_content = render_to_string('emails/rdv_confirmation.html', context)
    except Exception as e:
        logger.warning("[MAIL] Template introuvable, envoi texte brut : %s", e)
        html_content = None

    ligne_visio = f"\n🎥 Lien visioconférence : {jitsi_url}" if jitsi_url else ""
    text_content = (
        f"Bonjour {patient_nom},\n\n"
        f"Votre rendez-vous avec {medecin_nom} est {statut_display.lower()}.\n"
        f"Date : {date_str} à {heure_str}\n"
        + (f"Motif : {motif}\n" if motif else "")
        + ligne_visio
        + "\n\nMerci de vous présenter 10 minutes avant l'heure prévue.\n\n"
        "Cordialement,\nL'équipe CuraMedical"
    )

    sujet = f"CuraMedical — Votre rendez-vous du {rdv.date_heure.strftime('%d/%m/%Y')} est confirmé"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@curamedical.com')

    msg = EmailMultiAlternatives(sujet, text_content, from_email, [patient.email])
    if html_content:
        msg.attach_alternative(html_content, "text/html")
    try:
        msg.send(fail_silently=True)
        logger.info("[MAIL] Confirmation RDV envoyée à %s", patient.email)
    except Exception as e:
        logger.error("[MAIL] Erreur envoi à %s : %s", patient.email, e)


def _envoyer_whatsapp(*, telephone, patient_nom, medecin_nom, date_str, heure_str,
                      motif, is_visio, jitsi_url, nouveau_statut):
    sid   = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
    token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
    from_ = getattr(settings, 'TWILIO_WHATSAPP_FROM', '')

    if not (sid and token and from_):
        logger.warning("[WhatsApp] Twilio non configuré — notification ignorée.")
        return

    # Normaliser le numéro (ajouter whatsapp: et +212 si local)
    numero = telephone.strip()
    if not numero.startswith('+'):
        numero = '+212' + numero.lstrip('0')
    to_whatsapp = f"whatsapp:{numero}"

    statut_emoji = '✅' if nouveau_statut == 'CONFIRME' else '📌'
    statut_txt   = 'confirmé' if nouveau_statut == 'CONFIRME' else 'planifié'

    type_ligne = "📹 *Téléconsultation* (vidéo en ligne)" if is_visio else "🏥 *Cabinet* (présentiel)"

    corps = (
        f"{statut_emoji} *Rendez-vous {statut_txt} !*\n\n"
        f"Bonjour {patient_nom},\n\n"
        f"Votre rendez-vous a été *{statut_txt}* :\n\n"
        f"📅 {date_str} à *{heure_str}*\n"
        f"👨‍⚕️ {medecin_nom}\n"
        + (f"🩺 Motif : {motif}\n" if motif else "")
        + f"🏷️ Type  : {type_ligne}\n"
    )

    if jitsi_url:
        corps += (
            f"\n🎥 *Lien de votre vidéoconférence :*\n"
            f"{jitsi_url}\n\n"
            "📌 _Rejoignez ce lien à l'heure du rendez-vous._\n"
            "_Le médecin vous y attendra._"
        )
    else:
        corps += "\n_Merci de vous présenter 10 minutes avant l'heure prévue._"

    try:
        from twilio.rest import Client
        client = Client(sid, token)
        client.messages.create(
            body=corps,
            from_=f"whatsapp:{from_}",
            to=to_whatsapp,
        )
        logger.info("[WhatsApp] Notification envoyée à %s", numero)
    except Exception as e:
        logger.error("[WhatsApp] Erreur envoi notification à %s : %s", numero, e)
