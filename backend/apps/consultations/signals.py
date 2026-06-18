import logging

from celery import shared_task
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.common.tasks import dispatch_task
from .models import Consultation

logger = logging.getLogger(__name__)

SYMPTOM_LABELS = {
    'fever': 'Fièvre', 'high_fever': 'Fièvre élevée', 'mild_fever': 'Fièvre légère',
    'chills': 'Frissons', 'sweating': 'Transpiration excessive',
    'fatigue': 'Fatigue / Asthénie', 'lethargy': 'Léthargie',
    'cough': 'Toux', 'breathlessness': 'Difficulté respiratoire',
    'chest_pain': 'Douleur thoracique', 'headache': 'Maux de tête',
    'dizziness': 'Vertiges', 'nausea': 'Nausées', 'vomiting': 'Vomissements',
    'diarrhoea': 'Diarrhée', 'abdominal_pain': 'Douleur abdominale',
    'stomach_pain': 'Douleur gastrique', 'constipation': 'Constipation',
    'indigestion': 'Indigestion', 'back_pain': 'Douleur dorsale',
    'joint_pain': 'Douleurs articulaires', 'muscle_pain': 'Douleurs musculaires',
    'neck_stiffness': 'Raideur de nuque', 'skin_rash': 'Éruption cutanée',
    'itching': 'Démangeaisons', 'yellowish_skin': 'Jaunisse',
    'dark_urine': 'Urines foncées', 'weight_loss': 'Perte de poids',
    'loss_of_appetite': "Perte d'appétit", 'swollen_lymph_nodes': 'Ganglions gonflés',
    'runny_nose': 'Écoulement nasal', 'throat_irritation': 'Irritation de la gorge',
    'nasal_congestion': 'Congestion nasale', 'chest_congestion': 'Congestion thoracique',
    'mucoid_sputum': 'Expectorations mucoïdes', 'phlegm': 'Mucosités',
    'sneezing': 'Éternuements', 'shivering': 'Tremblements',
    'watering_from_eyes': 'Larmoiement', 'redness_of_eyes': 'Rougeur des yeux',
    'blurred_and_distorted_vision': 'Vision floue', 'visual_disturbances': 'Troubles visuels',
    'sunken_eyes': 'Yeux enfoncés', 'dehydration': 'Déshydratation',
    'excessive_hunger': 'Faim excessive', 'increased_appetite': 'Appétit augmenté',
    'polyuria': 'Polyurie (urines fréquentes)', 'burning_micturition': 'Brûlures urinaires',
    'spotting_urination': 'Urines irrégulières', 'bladder_discomfort': 'Inconfort vésical',
    'foul_smell_of_urine': 'Odeur urinaire anormale', 'continuous_feel_of_urine': 'Envies fréquentes d\'uriner',
    'swelling_of_stomach': 'Gonflement abdominal', 'distention_of_abdomen': 'Distension abdominale',
    'pain_during_bowel_movements': 'Douleur lors des selles', 'bloody_stool': 'Selles sanglantes',
    'passage_of_gases': 'Flatulences', 'irritability': 'Irritabilité',
    'depression': 'Dépression', 'anxiety': 'Anxiété',
    'mood_swings': "Sautes d'humeur", 'lack_of_concentration': 'Manque de concentration',
    'altered_sensorium': 'Confusion mentale', 'loss_of_balance': "Perte d'équilibre",
    'unsteadiness': 'Instabilité', 'slurred_speech': 'Élocution difficile',
    'weakness_in_limbs': 'Faiblesse des membres', 'weakness_of_one_body_side': "Faiblesse d'un côté",
    'movement_stiffness': 'Raideur articulaire', 'cramps': 'Crampes',
    'swollen_legs': 'Jambes gonflées', 'swollen_blood_vessels': 'Veines gonflées',
    'prominent_veins_on_calf': 'Veines saillantes sur le mollet',
    'bruising': 'Ecchymoses', 'pus_filled_pimples': 'Boutons avec pus',
    'blackheads': 'Points noirs', 'scurring': 'Cicatrices',
    'skin_peeling': 'Desquamation cutanée', 'silver_like_dusting': 'Pellicules argentées',
    'small_dents_in_nails': 'Petits trous dans les ongles', 'inflammatory_nails': 'Ongles enflammés',
    'blister': 'Ampoule / Vésicule', 'red_sore_around_nose': 'Rougeur autour du nez',
    'yellow_crust_ooze': 'Croûtes jaunes', 'dischromic_patches': 'Taches décolorées',
    'red_spots_over_body': 'Taches rouges sur le corps', 'rusty_sputum': 'Expectorations rouillées',
    'fast_heart_rate': 'Tachycardie (cœur rapide)', 'palpitations': 'Palpitations',
    'irregular_sugar_level': 'Glycémie irrégulière', 'obesity': 'Obésité',
    'enlarged_thyroid': 'Thyroïde élargie', 'brittle_nails': 'Ongles cassants',
    'swollen_extremities': 'Extrémités gonflées', 'puffy_face_and_eyes': 'Visage et yeux gonflés',
    'cold_hands_and_feets': 'Mains et pieds froids', 'drying_and_tingling_lips': 'Lèvres sèches/picotements',
    'slippery_image_in_throat': 'Sensation de glissement dans la gorge',
    'patches_in_throat': 'Plaques dans la gorge', 'high_joint_pain': 'Douleur articulaire intense',
    'painful_walking': 'Douleur à la marche', 'hip_joint_pain': 'Douleur de la hanche',
    'knee_pain': 'Douleur du genou', 'swelling_joints': 'Articulations gonflées',
    'stiff_neck': 'Nuque raide', 'spinning_movements': 'Sensations de rotation',
    'loss_of_smell': 'Perte de l\'odorat', 'mucus_in_stool': 'Mucus dans les selles',
    'stomach_bleeding': 'Saignement gastrique', 'acute_liver_failure': 'Insuffisance hépatique aiguë',
    'fluid_overload': 'Surcharge hydrique', 'swelling_of_stomach': 'Gonflement de l\'estomac',
    'history_of_alcohol_consumption': 'Antécédents de consommation d\'alcool',
}


def _translate_symptoms(symptomes):
    """Traduit une liste de clés de symptômes en libellés français."""
    if not symptomes:
        return None
    if isinstance(symptomes, list):
        labels = [SYMPTOM_LABELS.get(s, s.replace('_', ' ').capitalize()) for s in symptomes if s]
        return ', '.join(labels) if labels else None
    return str(symptomes)


@receiver(post_save, sender=Consultation)
def trigger_consultation_notifications(sender, instance, created, **kwargs):
    if not created:
        return
    dispatch_task(notify_consultation_task, instance.pk)


@shared_task(name='consultations.notify_email')
def notify_consultation_task(consultation_pk):
    try:
        consultation = Consultation.objects.select_related('patient', 'medecin').get(pk=consultation_pk)
    except Consultation.DoesNotExist:
        return

    patient  = consultation.patient
    medecin  = consultation.medecin
    date_str = consultation.date_consultation.strftime('%d/%m/%Y à %H:%M')
    salutation = "M." if patient.sexe == 'M' else "Mme"

    pdf_bytes = None
    try:
        from .report_generator import generate_consultation_report_pdf
        pdf_bytes = generate_consultation_report_pdf(consultation).getvalue()
    except Exception as e:
        logger.error("[Consultation] PDF échoué: %s", e)

    _send_email(patient, medecin, consultation, date_str, salutation, pdf_bytes)


def _send_email(patient, medecin, consultation, date_str, salutation, pdf_bytes):
    if not getattr(patient, 'email', None):
        logger.warning("[Consultation] Patient %s sans email — mail ignoré.", patient.nom_complet)
        return
    try:
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.conf import settings

        base_url    = getattr(settings, 'PUBLIC_BASE_URL', '').rstrip('/')
        portal_url  = f"{base_url}/login" if base_url else None
        symptomes_fr = _translate_symptoms(consultation.symptomes)

        context = {
            'salutation':      salutation,
            'patient_nom':     patient.nom_complet,
            'medecin_nom':     medecin.get_full_name(),
            'date_str':        date_str,
            'diagnostic':      consultation.diagnostic or 'Non renseigné',
            'symptomes':       symptomes_fr,
            'examen_clinique': consultation.examen_clinique or None,
            'notes':           consultation.notes or None,
            'portal_url':      portal_url,
        }

        subject   = f"CuraMedical — Compte rendu du {consultation.date_consultation.strftime('%d/%m/%Y')}"
        html_body = render_to_string('emails/consultation_report.html', context)
        text_body = (
            f"Bonjour {salutation} {patient.nom_complet},\n\n"
            f"Votre compte rendu de consultation du {date_str} "
            f"établi par Dr. {medecin.get_full_name()} est disponible.\n\n"
            f"Diagnostic : {context['diagnostic']}\n"
            + (f"Symptômes : {symptomes_fr}\n" if symptomes_fr else "")
            + (f"Examen clinique : {consultation.examen_clinique}\n" if consultation.examen_clinique else "")
            + (f"Notes : {consultation.notes}\n" if consultation.notes else "")
            + "\nLe compte rendu complet est joint en PDF.\n\n"
            "Cordialement,\nL'équipe CuraMedical"
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[patient.email],
        )
        email.attach_alternative(html_body, "text/html")
        if pdf_bytes:
            email.attach(f"compte_rendu_{consultation.pk}.pdf", pdf_bytes, 'application/pdf')
        email.send(fail_silently=False)
        logger.info("[Consultation] Email envoyé à %s", patient.email)
    except Exception as e:
        logger.error("[Consultation] Email échoué (%s): %s", getattr(patient, 'email', '?'), e)
