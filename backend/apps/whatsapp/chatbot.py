"""
CuraMedical WhatsApp Chatbot — Propulsé par LLaMA 3.3 70B via Groq.

Le LLM comprend n'importe quelle formulation naturelle (français, arabe, anglais…)
et extrait les entités (date, heure, motif, symptômes) en une seule passe.
La logique métier (BDD, PDF, Twilio) reste en Python.
"""
import json
import logging
import re
from datetime import datetime, timedelta, date

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

# ── États de conversation ──────────────────────────────────────────────────────
IDLE              = 'idle'
BOOKING_DATE      = 'booking_date'
BOOKING_TIME      = 'booking_time'
BOOKING_MOTIF     = 'booking_motif'
BOOKING_TYPE      = 'booking_type'
BOOKING_CONFIRM   = 'booking_confirm'
CHOOSE_ORDONNANCE = 'choose_ordonnance'

# Intents qui interrompent un flux multi-tours
INTERRUPTIBLE_INTENTS = {'ordonnance', 'consultation', 'mes_rdv', 'menu', 'annuler_rdv', 'symptoms', 'greetings'}

_LLM_SYSTEM = """\
Tu es l'assistant WhatsApp de CuraMedical, une clinique médicale moderne.
Tu réponds toujours en français, de façon naturelle, chaleureuse et concise (max 3 lignes pour les réponses directes).
Pour les urgences médicales, toujours conseiller d'appeler le 15 (SAMU).
Tu n'es pas médecin — ne pose jamais de diagnostic définitif.

Date d'aujourd'hui : {today}
Patient connecté : {patient}

Analyse le message et retourne UNIQUEMENT un objet JSON valide avec cette structure exacte :
{{
  "intent": "<intent>",
  "reply": "<réponse directe en français, ou null>",
  "rdv_data": {{"date": "<YYYY-MM-DD ou null>", "heure": <entier ou null>, "motif": "<texte ou null>", "type": "<PRESENTIEL|EN_LIGNE|null>"}},
  "symptoms": ["<symptome1>", "<symptome2>"]
}}

Valeurs possibles pour intent :
- "rdv"          → l'utilisateur veut PRENDRE un nouveau rendez-vous
- "mes_rdv"      → l'utilisateur veut VOIR ses rendez-vous existants
- "modifier_rdv" → l'utilisateur veut MODIFIER/CHANGER/DÉPLACER/REPORTER un rendez-vous existant (imprévu, changer date, heure ou type)
- "annuler_rdv"  → l'utilisateur veut ANNULER/SUPPRIMER définitivement un rendez-vous
- "ordonnance"   → l'utilisateur veut recevoir son ordonnance
- "consultation" → l'utilisateur veut son compte rendu de consultation
- "symptoms"     → l'utilisateur décrit des symptômes médicaux
- "menu"         → l'utilisateur veut voir les options disponibles
- "oui"          → confirmation dans un dialogue en cours
- "non"          → refus/annulation dans un dialogue en cours
- "greetings"    → salutation (génère une réponse chaleureuse dans reply)
- "autre"        → tout autre message (génère une réponse utile dans reply)

IMPORTANT : "modifier" ≠ "annuler". Si l'utilisateur dit "j'ai un imprévu", "décaler", "reporter", "changer", "modifier" → intent="modifier_rdv". Seulement si l'utilisateur dit explicitement "annuler", "supprimer", "cancel" → intent="annuler_rdv".

Pour "rdv" : extrais date, heure, motif et type si mentionnés dans le message.
Pour "symptoms" : liste les symptômes en français dans le tableau symptoms.
Pour "greetings" et "autre" : génère une réponse naturelle dans reply.
"""

# Traductions maladies EN → FR (enrichies)
EN_TO_FR_DISEASE = {
    # Maladies courantes
    'Fungal infection': 'Infection fongique',
    'Allergy': 'Allergie',
    'GERD': 'Reflux gastro-œsophagien',
    'Chronic cholestasis': 'Cholestase chronique',
    'Drug Reaction': 'Réaction médicamenteuse',
    'Peptic ulcer diseae': 'Ulcère gastro-duodénal',
    'AIDS': 'SIDA',
    'Diabetes ': 'Diabète',
    'Gastroenteritis': 'Gastro-entérite',
    'Bronchial Asthma': 'Asthme bronchique',
    'Hypertension ': 'Hypertension artérielle',
    'Migraine': 'Migraine',
    'Cervical spondylosis': 'Spondylose cervicale',
    'Paralysis (brain hemorrhage)': 'Paralysie (hémorragie cérébrale)',
    'Jaundice': 'Jaunisse (Ictère)',
    'Malaria': 'Paludisme',
    'Chicken pox': 'Varicelle',
    'Dengue': 'Dengue',
    'Typhoid': 'Typhoïde',
    'hepatitis A': 'Hépatite A',
    'Hepatitis B': 'Hépatite B',
    'Hepatitis C': 'Hépatite C',
    'Hepatitis D': 'Hépatite D',
    'Hepatitis E': 'Hépatite E',
    'Alcoholic hepatitis': 'Hépatite alcoolique',
    'Tuberculosis': 'Tuberculose',
    'Common Cold': 'Rhume commun',
    'Pneumonia': 'Pneumonie',
    'Dimorphic hemmorhoids(piles)': 'Hémorroïdes',
    'Heart attack': 'Crise cardiaque',
    'Varicose veins': 'Varices',
    'Hypothyroidism': 'Hypothyroïdie',
    'Hyperthyroidism': 'Hyperthyroïdie',
    'Hypoglycemia': 'Hypoglycémie',
    'Osteoarthritis': 'Arthrose',
    'Arthritis': 'Arthrite',
    '(vertigo) Paroymsal  Positional Vertigo': 'Vertige positionnel bénin',
    'Acne': 'Acné',
    'Urinary tract infection': 'Infection urinaire',
    'Psoriasis': 'Psoriasis',
    'Impetigo': 'Impétigo',
    'viral warts': 'Verrues virales',
    # Ajouts pour les cas fréquents de fever+cough
    'kidney failure': 'Insuffisance rénale',
    'Kidney failure': 'Insuffisance rénale',
    'liver cancer': 'Cancer du foie',
    'Liver cancer': 'Cancer du foie',
    'marijuana abuse': 'Intoxication (substance)',
    'Marijuana abuse': 'Intoxication (substance)',
    'flu': 'Grippe',
    'Flu': 'Grippe',
    'Influenza': 'Grippe',
    'Sinusitis': 'Sinusite',
    'Bronchitis': 'Bronchite',
    'Upper respiratory infection': 'Infection respiratoire haute',
    # Maladies retournées en minuscules / non traduites par le service IA
    'common cold': 'Rhume commun',
    'thyroid nodule': 'Nodule thyroïdien',
    'Thyroid nodule': 'Nodule thyroïdien',
    'hydrocele of the testicle': 'Hydrocèle testiculaire',
    'Hydrocele of the testicle': 'Hydrocèle testiculaire',
    'melanoma': 'Mélanome',
    'Melanoma': 'Mélanome',
    'breast infection (mastitis)': 'Infection mammaire (mastite)',
    'impulse control disorder': 'Trouble du contrôle des impulsions',
    'chronic fatigue syndrome': 'Syndrome de fatigue chronique',
    'sleep apnea': 'Apnée du sommeil',
    'tension headache': 'Céphalées de tension',
    'food poisoning': 'Intoxication alimentaire',
    'urinary tract infection': 'Infection urinaire',
    'strep throat': 'Angine streptococcique',
    'Appendicitis': 'Appendicite',
    'Meningitis': 'Méningite',
    'Anemia': 'Anémie',
    'Sepsis': 'Sepsis',
    'Epilepsy': 'Épilepsie',
    'Depression': 'Dépression',
    'Anxiety': 'Anxiété',
    'Obesity': 'Obésité',
    'Gout': 'Goutte',
    'Eczema': 'Eczéma',
    'Lupus': 'Lupus',
    'Stroke': 'AVC',
    'Pneumonia': 'Pneumonie',
    'Tuberculosis': 'Tuberculose',
    'Malaria': 'Paludisme',
}

# Traductions symptômes EN → FR
EN_TO_FR_SYMPTOM = {
    'fever': 'fièvre', 'cough': 'toux', 'headache': 'maux de tête',
    'fatigue': 'fatigue', 'nausea': 'nausées', 'vomiting': 'vomissements',
    'diarrhea': 'diarrhée', 'diarrhoea': 'diarrhée',
    'joint_pain': 'douleurs articulaires', 'joint pain': 'douleurs articulaires',
    'skin_rash': 'éruption cutanée', 'skin rash': 'éruption cutanée',
    'shortness of breath': 'essoufflement', 'breathlessness': 'essoufflement',
    'chest_pain': 'douleur thoracique', 'chest pain': 'douleur thoracique',
    'back_pain': 'douleur dorsale', 'back pain': 'douleur dorsale',
    'abdominal_pain': 'douleur abdominale', 'abdominal pain': 'douleur abdominale',
    'weight_loss': 'perte de poids', 'weight loss': 'perte de poids',
    'loss_of_appetite': "perte d'appétit", 'loss of appetite': "perte d'appétit",
    'sweating': 'transpiration', 'chills': 'frissons', 'dizziness': 'vertiges',
    'swollen_lymph_nodes': 'ganglions gonflés', 'yellowish_skin': 'jaunisse',
    'high_fever': 'fièvre élevée', 'high fever': 'fièvre élevée',
    'mild_fever': 'fièvre légère', 'mild fever': 'fièvre légère',
    'lethargy': 'léthargie', 'neck_stiffness': 'raideur nuque',
    'skin_rash': 'éruption cutanée', 'itching': 'démangeaisons',
    'dark_urine': 'urines foncées', 'loss_of_appetite': "perte d'appétit",
    'fast_heart_rate': 'palpitations', 'burning_micturition': 'brûlure miction',
    'redness_of_eyes': 'yeux rouges', 'throat_irritation': 'irritation gorge',
    'runny_nose': 'écoulement nasal', 'constipation': 'constipation',
    'indigestion': 'indigestion', 'muscle_pain': 'douleurs musculaires',
    'joint_pain': 'douleurs articulaires', 'stomach_pain': 'douleur gastrique',
}


class WhatsAppChatbot:
    """Point d'entrée principal du chatbot. Instancier avec une conversation."""

    def __init__(self, conversation):
        self.conv = conversation
        self.patient = conversation.patient
        self.media_url = None   # rempli quand un PDF doit être joint au TwiML

    def process(self, message: str) -> str:
        msg = message.strip()
        state = self.conv.state

        # ── Compréhension par LLaMA ───────────────────────────────────────────
        llm = self._llm_understand(msg, state)
        intent = llm.get('intent', 'autre')
        logger.debug("[LLM] intent=%s state=%s msg=%.60s", intent, state, msg)

        # ── Flux multi-tours ──────────────────────────────────────────────────
        if state != IDLE:
            # Annulation universelle
            if intent == 'non':
                self._set_state(IDLE, {})
                return "❌ Action annulée. Tapez *menu* pour voir les options."

            # Intents qui n'ont rien à voir avec le flux en cours → échappatoire
            ESCAPE_INTENTS = {'ordonnance', 'consultation', 'mes_rdv', 'menu', 'annuler_rdv', 'modifier_rdv'}
            if intent in ESCAPE_INTENTS:
                self._set_state(IDLE, {})
                # on laisse tomber dans les handlers ci-dessous

            else:
                # Logique spécifique par étape
                if state == BOOKING_DATE:
                    return self._booking_date_smart(msg, llm)

                if state == BOOKING_TIME:
                    return self._booking_time_smart(msg, llm)

                if state == BOOKING_MOTIF:
                    # "fièvre et toux" = motif du RDV, pas une analyse de symptômes
                    if intent == 'symptoms':
                        symptoms = llm.get('symptoms') or []
                        motif = ', '.join(symptoms) if symptoms else msg
                        return self._booking_motif(motif)
                    return self._booking_motif(msg)

                if state == BOOKING_TYPE:
                    # "je veux un rdv vidéo" = type EN_LIGNE, pas un nouveau RDV
                    if intent == 'rdv':
                        rd = llm.get('rdv_data') or {}
                        if rd.get('type'):
                            return self._booking_type(rd['type'].lower())
                    return self._booking_type(msg)

                if state == BOOKING_CONFIRM:
                    return self._booking_confirm(msg)

                if state == CHOOSE_ORDONNANCE:
                    return self._choose_ordonnance(msg)

        handlers = {
            'greetings':    lambda: llm.get('reply') or self._greetings(),
            'menu':         self._menu,
            'rdv':          lambda: self._start_booking_smart(msg, llm),
            'mes_rdv':      self._mes_rdv,
            'modifier_rdv': lambda: self._modifier_rdv(llm),
            'annuler_rdv':  self._annuler_rdv,
            'ordonnance':   self._ordonnance,
            'consultation': self._consultation,
            'symptoms':     lambda: self._symptoms_llm(llm) or self._symptoms(msg),
        }
        handler = handlers.get(intent)
        if handler:
            return handler()

        # Fallback : réponse directe du LLM
        return llm.get('reply') or self._default_reply()

    # ═══════════════════════════════════════════════════════════════════════════
    # ACCUEIL / MENU
    # ═══════════════════════════════════════════════════════════════════════════

    def _greetings(self) -> str:
        name = f" {self.patient.prenom}" if self.patient else ""
        return (
            f"👋 Bonjour{name} ! Je suis l'assistant médical de *CuraMedical*.\n\n"
            + self._menu_body()
        )

    def _menu(self) -> str:
        return "📋 *Menu CuraMedical*\n\n" + self._menu_body()

    def _menu_body(self) -> str:
        return (
            "Voici ce que je peux faire :\n\n"
            "🗓️  *rendez-vous* — Prendre un rendez-vous\n"
            "📅  *mes rdv* — Voir mes prochains rendez-vous\n"
            "✏️  *modifier mon rdv* — Modifier date, heure ou type\n"
            "❌  *annuler mon rdv* — Annuler un rendez-vous\n"
            "💊  *mon ordonnance* — Recevoir votre ordonnance en PDF\n"
            "📋  *ma consultation* — Recevoir votre compte rendu de consultation en PDF\n"
            "🔬  Décrivez vos *symptômes* pour une analyse IA\n\n"
            "_Tapez ou dites simplement ce que vous souhaitez._"
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # PRISE DE RENDEZ-VOUS (state machine 4 étapes)
    # ═══════════════════════════════════════════════════════════════════════════

    def _start_booking(self) -> str:
        self._set_state(BOOKING_DATE, {})
        return (
            "🗓️ *Prise de rendez-vous*\n\n"
            "Pour quelle *date* souhaitez-vous un rendez-vous ?\n\n"
            "_Ex : demain, lundi, 25/05, dans 3 jours_"
        )

    def _booking_date(self, msg: str) -> str:
        parsed = self._parse_date(msg)
        if not parsed:
            return (
                "❌ Je n'ai pas compris la date.\n"
                "Essayez : *demain*, *lundi*, *25/05*, *dans 3 jours*."
            )
        label = self._format_date(parsed)
        self._set_state(BOOKING_TIME, {'date': parsed.isoformat(), 'date_label': label})
        return (
            f"✅ Date : *{label}*\n\n"
            "À quelle *heure* préférez-vous ?\n\n"
            "_Ex : 9h, 14h30, matin, après-midi, soir_"
        )

    def _booking_time(self, msg: str) -> str:
        hour = self._parse_time(msg)
        data = {**self.conv.state_data, 'heure': hour, 'heure_label': msg.strip()}
        self._set_state(BOOKING_MOTIF, data)
        return (
            "Quel est le *motif* de votre visite ?\n\n"
            "_Ex : fièvre, douleur abdominale, suivi, renouvellement ordonnance_"
        )

    def _booking_motif(self, msg: str) -> str:
        data = {**self.conv.state_data, 'motif': msg.strip()}
        self._set_state(BOOKING_TYPE, data)
        return (
            "Quel type de consultation souhaitez-vous ?\n\n"
            "1️⃣ *Cabinet* — consultation en présentiel\n"
            "2️⃣ *Téléconsultation* — consultation vidéo en ligne\n\n"
            "_Répondez_ *1* _ou_ *cabinet* / *2* _ou_ *vidéo*"
        )

    def _booking_type(self, msg: str) -> str:
        m = msg.lower().strip()
        if m in ('1', 'cabinet', 'présentiel', 'presentiel', 'physique'):
            type_consult = 'PRESENTIEL'
            type_label   = '🏥 Cabinet (présentiel)'
        elif m in ('2', 'vidéo', 'video', 'ligne', 'en ligne', 'téléconsultation',
                   'teleconsultation', 'visio', 'online'):
            type_consult = 'EN_LIGNE'
            type_label   = '📹 Téléconsultation (vidéo)'
        else:
            return (
                "Je n'ai pas compris. Répondez :\n"
                "*1* pour Cabinet  /  *2* pour Téléconsultation"
            )
        data = {**self.conv.state_data, 'type_consultation': type_consult, 'type_label': type_label}
        self._set_state(BOOKING_CONFIRM, data)
        return (
            f"📋 *Récapitulatif de votre demande :*\n\n"
            f"📅 Date        : {data['date_label']}\n"
            f"⏰ Heure       : {data['heure_label']}\n"
            f"🩺 Motif       : {data['motif']}\n"
            f"🏥 Type        : {type_label}\n\n"
            "Confirmez-vous ? Répondez *oui* ou *non*."
        )

    def _booking_confirm(self, msg: str) -> str:
        m = msg.lower().strip()
        is_oui = any(w in m for w in ['oui', 'yes', 'ok', "d'accord", 'confirme', 'c est bon', 'ça marche', 'valide'])
        is_non = any(w in m for w in ['non', 'no', 'annule', 'cancel', 'pas bon'])
        if is_non:
            self._set_state(IDLE, {})
            return "❌ Annulé. Tapez *menu* pour voir les options."
        if not is_oui:
            return "Répondez *oui* pour confirmer ou *non* pour annuler."
        data = self.conv.state_data
        self._set_state(IDLE, {})
        # Modification d'un RDV existant si rdv_id présent
        if data.get('rdv_id'):
            return self._update_rdv(data)
        return self._create_rdv(data)

    def _create_rdv(self, data: dict) -> str:
        from apps.users.models import User
        from apps.appointments.models import RendezVous

        if not self.patient:
            return (
                "⚠️ Votre numéro n'est pas encore associé à un dossier patient.\n"
                "Contactez la clinique pour finaliser :\n"
                "📞 +212 5 22 00 00 00"
            )
        try:
            medecin = User.objects.filter(role='medecin', is_active=True).first()
            if not medecin:
                raise ValueError("Aucun médecin actif")

            from zoneinfo import ZoneInfo
            tz_casa = ZoneInfo('Africa/Casablanca')
            rdv_date = datetime.fromisoformat(data['date'])
            hour = data.get('heure', 9)
            rdv_dt = rdv_date.replace(hour=int(hour), minute=0, second=0, microsecond=0, tzinfo=tz_casa)

            rdv = RendezVous.objects.create(
                patient=self.patient,
                medecin=medecin,
                date_heure=rdv_dt,
                motif=data.get('motif', 'Consultation générale'),
                statut='DEMANDE',
                type_consultation=data.get('type_consultation', 'PRESENTIEL'),
            )
            type_icon = '📹' if rdv.type_consultation == 'EN_LIGNE' else '🏥'
            type_txt  = 'Téléconsultation' if rdv.type_consultation == 'EN_LIGNE' else 'Cabinet'

            msg = (
                f"✅ *Demande enregistrée !*\n\n"
                f"📅 {self._format_datetime(rdv_dt)}\n"
                f"🩺 Motif  : {rdv.motif}\n"
                f"{type_icon} Type   : {type_txt}\n"
                f"👨‍⚕️ Dr. {medecin.get_full_name()}\n"
                f"🔖 Référence : *#{rdv.id}*"
            )

            if rdv.type_consultation == 'EN_LIGNE' and rdv.lien_visio:
                jitsi_url = f"https://meet.jit.si/{rdv.lien_visio}"
                msg += (
                    f"\n\n🎥 *Lien de votre vidéoconférence :*\n"
                    f"{jitsi_url}\n\n"
                    f"📌 _Rejoignez ce lien à l'heure du rendez-vous._\n"
                    f"_Le médecin vous y attendra._"
                )
            else:
                msg += "\n\nVous serez contacté(e) pour confirmation."

            return msg
        except Exception as e:
            logger.error("[WhatsApp] Création RDV échouée: %s", e)
            return (
                "✅ Votre demande a été reçue.\n"
                "Notre équipe vous contactera pour confirmer.\n"
                "📞 +212 5 22 00 00 00"
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # MES RENDEZ-VOUS
    # ═══════════════════════════════════════════════════════════════════════════

    def _mes_rdv(self) -> str:
        if not self.patient:
            return self._not_registered()
        from apps.appointments.models import RendezVous
        from django.utils import timezone

        rdvs = RendezVous.objects.filter(
            patient=self.patient,
            date_heure__gte=timezone.now(),
            statut__in=['DEMANDE', 'PLANIFIE', 'CONFIRME'],
        ).order_by('date_heure')[:5]

        if not rdvs:
            return (
                "📅 Vous n'avez pas de rendez-vous à venir.\n\n"
                "Tapez *rendez-vous* pour en prendre un."
            )

        ICON = {'DEMANDE': '⏳', 'PLANIFIE': '📌', 'CONFIRME': '✅'}
        lines = ["📅 *Vos prochains rendez-vous :*\n"]
        for rdv in rdvs:
            icon = ICON.get(rdv.statut, '•')
            lines.append(
                f"{icon} *{self._format_datetime(rdv.date_heure)}*\n"
                f"   👨‍⚕️ Dr. {rdv.medecin.get_full_name()} — _{rdv.motif}_"
            )
        return "\n\n".join(lines)

    # ═══════════════════════════════════════════════════════════════════════════
    # ANNULATION RDV
    # ═══════════════════════════════════════════════════════════════════════════

    def _annuler_rdv(self) -> str:
        # Si on est en plein flux de booking, annuler le flux
        if self.conv.state != IDLE:
            self._set_state(IDLE, {})
            return "✅ Action annulée."

        if not self.patient:
            return self._not_registered()

        from apps.appointments.models import RendezVous
        from django.utils import timezone

        rdv = RendezVous.objects.filter(
            patient=self.patient,
            date_heure__gte=timezone.now(),
            statut__in=['DEMANDE', 'PLANIFIE', 'CONFIRME'],
        ).order_by('date_heure').first()

        if not rdv:
            return "Vous n'avez pas de rendez-vous actif à annuler."

        rdv.statut = 'ANNULE'
        rdv.save(update_fields=['statut', 'modifie_le'])
        return (
            f"✅ Rendez-vous du *{self._format_datetime(rdv.date_heure)}* annulé.\n\n"
            "Tapez *rendez-vous* pour en prendre un nouveau."
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # MODIFICATION RDV
    # ═══════════════════════════════════════════════════════════════════════════

    def _modifier_rdv(self, llm: dict | None = None) -> str:
        if not self.patient:
            return self._not_registered()

        from apps.appointments.models import RendezVous
        from django.utils import timezone

        rdv = RendezVous.objects.filter(
            patient=self.patient,
            date_heure__gte=timezone.now(),
            statut__in=['DEMANDE', 'PLANIFIE', 'CONFIRME'],
        ).order_by('date_heure').first()

        if not rdv:
            return (
                "📅 Vous n'avez pas de rendez-vous actif à modifier.\n\n"
                "Tapez *rendez-vous* pour en prendre un nouveau."
            )

        type_label = '📹 Téléconsultation' if rdv.type_consultation == 'EN_LIGNE' else '🏥 Cabinet'
        data = {
            'rdv_id':            rdv.id,
            'motif':             rdv.motif,
            'type_consultation': rdv.type_consultation,
            'type_label':        type_label,
        }

        # Pré-remplir depuis les entités extraites du message de modification
        if llm:
            rd = llm.get('rdv_data') or {}
            if rd.get('date'):
                try:
                    dt = datetime.fromisoformat(rd['date'])
                    data['date'] = rd['date']
                    data['date_label'] = self._format_date(dt)
                except Exception:
                    pass
            if rd.get('heure') is not None:
                data['heure'] = rd['heure']
                data['heure_label'] = f"{rd['heure']}h"
            if rd.get('type') in ('PRESENTIEL', 'EN_LIGNE'):
                data['type_consultation'] = rd['type']
                data['type_label'] = '🏥 Cabinet' if rd['type'] == 'PRESENTIEL' else '📹 Téléconsultation'

        current_summary = (
            f"✏️ *Modification de votre rendez-vous*\n\n"
            f"📋 Rendez-vous actuel :\n"
            f"📅 {self._format_datetime(rdv.date_heure)}\n"
            f"🩺 Motif : {rdv.motif}\n"
            f"🏥 Type  : {type_label}\n\n"
        )

        if not data.get('date'):
            self._set_state(BOOKING_DATE, data)
            return current_summary + "Quelle est la *nouvelle date* souhaitée ?\n_Ex : demain, lundi, 25/05_"
        if data.get('heure') is None:
            self._set_state(BOOKING_TIME, data)
            return current_summary + f"✅ Date : *{data['date_label']}*\n\nÀ quelle *heure* ?\n_Ex : 9h, 14h30_"
        # motif et type sont déjà pré-remplis → aller directement au récap
        self._set_state(BOOKING_CONFIRM, data)
        return current_summary + self._recap_rdv(data)

    def _update_rdv(self, data: dict) -> str:
        from apps.appointments.models import RendezVous
        from django.utils import timezone as tz

        try:
            from zoneinfo import ZoneInfo
            tz_casa = ZoneInfo('Africa/Casablanca')
            rdv = RendezVous.objects.get(pk=data['rdv_id'])
            rdv_date = datetime.fromisoformat(data['date'])
            # Heure par défaut = heure du RDV original en heure Casablanca
            default_hour = rdv.date_heure.astimezone(tz_casa).hour
            hour = data.get('heure', default_hour)
            rdv_dt = rdv_date.replace(hour=int(hour), minute=0, second=0, microsecond=0, tzinfo=tz_casa)

            old_dt = rdv.date_heure
            rdv.date_heure = rdv_dt
            rdv.type_consultation = data.get('type_consultation', rdv.type_consultation)
            rdv.motif = data.get('motif', rdv.motif)
            rdv.save(update_fields=['date_heure', 'type_consultation', 'motif', 'lien_visio', 'modifie_le'])

            type_label = '📹 Téléconsultation' if rdv.type_consultation == 'EN_LIGNE' else '🏥 Cabinet'
            return (
                f"✅ *Rendez-vous modifié avec succès !*\n\n"
                f"📅 Ancienne date : ~~{self._format_datetime(old_dt)}~~\n"
                f"📅 Nouvelle date : *{self._format_datetime(rdv_dt)}*\n"
                f"🩺 Motif : {rdv.motif}\n"
                f"🏥 Type  : {type_label}\n\n"
                "La clinique vous confirmera la modification."
            )
        except Exception as e:
            logger.error("[WhatsApp] Modification RDV échouée : %s", e)
            return "❌ Impossible de modifier le rendez-vous. Contactez la clinique : 📞 +212 5 22 00 00 00"

    # ═══════════════════════════════════════════════════════════════════════════
    # ORDONNANCE PDF
    # ═══════════════════════════════════════════════════════════════════════════

    def _ordonnance(self) -> str:
        if not self.patient:
            return self._not_registered()

        prescriptions = list(
            self.patient.prescriptions.prefetch_related('lignes').order_by('-cree_le')[:3]
        )
        if not prescriptions:
            return "💊 Vous n'avez pas d'ordonnance enregistrée pour le moment."

        if len(prescriptions) == 1:
            return self._send_ordonnance_pdf(prescriptions[0])

        # Plusieurs ordonnances — laisser le patient choisir
        ids = [p.id for p in prescriptions]
        self._set_state(CHOOSE_ORDONNANCE, {'ids': ids})
        lines = ["💊 *Vos ordonnances disponibles :*\n"]
        for i, p in enumerate(prescriptions, 1):
            lines.append(
                f"*{i}.* {p.cree_le.strftime('%d/%m/%Y')} "
                f"— Dr. {p.medecin.get_full_name()}"
            )
        lines.append("\nRépondez avec le numéro (*1*, *2* ou *3*) ou *dernière* pour la plus récente.")
        return "\n".join(lines)

    def _choose_ordonnance(self, msg: str) -> str:
        ids = self.conv.state_data.get('ids', [])
        self._set_state(IDLE, {})

        index = 0
        msg_l = msg.lower().strip()
        if 'dernière' in msg_l or 'derniere' in msg_l or msg_l == '1':
            index = 0
        elif msg_l == '2':
            index = 1
        elif msg_l == '3':
            index = 2
        else:
            m = re.search(r'\d', msg_l)
            if m:
                index = int(m.group()) - 1

        if not ids or index >= len(ids):
            return "❌ Choix invalide. Tapez *ordonnance* pour réessayer."

        from apps.prescriptions.models import Prescription
        try:
            prescription = Prescription.objects.prefetch_related('lignes').get(id=ids[index])
            return self._send_ordonnance_pdf(prescription)
        except Prescription.DoesNotExist:
            return "❌ Ordonnance introuvable. Contactez la clinique."

    def _send_ordonnance_pdf(self, prescription) -> str:
        from apps.prescriptions.pdf_generator import generate_prescription_pdf

        try:
            pdf_buffer = generate_prescription_pdf(prescription)
            filename = f"prescriptions/ordonnance_{prescription.id}.pdf"

            if default_storage.exists(filename):
                default_storage.delete(filename)
            saved_path = default_storage.save(filename, ContentFile(pdf_buffer.read()))

            base_url = getattr(settings, 'PUBLIC_BASE_URL', '').rstrip('/')
            if not base_url:
                raise ValueError("PUBLIC_BASE_URL non configuré")

            self.media_url = f"{base_url}{settings.MEDIA_URL}{saved_path}"

            meds = prescription.lignes.all()[:5]
            med_lines = "\n".join(
                f"  • {l.medicament} {l.dosage} — {l.frequence} pendant {l.duree}"
                for l in meds
            )
            return (
                f"💊 *Ordonnance du {prescription.cree_le.strftime('%d/%m/%Y')}*\n"
                f"👨‍⚕️ Dr. {prescription.medecin.get_full_name()}\n\n"
                f"*Médicaments prescrits :*\n{med_lines}"
            )
        except Exception as e:
            logger.error("[WhatsApp] Envoi ordonnance PDF: %s", e)
            return (
                "❌ Erreur lors de l'envoi du PDF.\n"
                "Contactez la clinique : 📞 +212 5 22 00 00 00"
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # DERNIÈRE CONSULTATION
    # ═══════════════════════════════════════════════════════════════════════════

    def _consultation(self) -> str:
        if not self.patient:
            return self._not_registered()

        consultation = (
            self.patient.consultations
            .select_related('medecin')
            .order_by('-date_consultation')
            .first()
        )
        if not consultation:
            return "📋 Vous n'avez pas de consultation enregistrée."

        return self._send_consultation_pdf(consultation)

    def _send_consultation_pdf(self, consultation) -> str:
        from apps.consultations.report_generator import generate_consultation_report_pdf

        try:
            pdf_buffer = generate_consultation_report_pdf(consultation)
            filename = f"consultations/compte_rendu_{consultation.pk}.pdf"

            if default_storage.exists(filename):
                default_storage.delete(filename)
            saved_path = default_storage.save(filename, ContentFile(pdf_buffer.read()))

            base_url = getattr(settings, 'PUBLIC_BASE_URL', '').rstrip('/')
            if not base_url:
                raise ValueError("PUBLIC_BASE_URL non configuré")

            self.media_url = f"{base_url}{settings.MEDIA_URL}{saved_path}"

            date_str = consultation.date_consultation.strftime('%d/%m/%Y')
            symptomes = consultation.symptomes
            if isinstance(symptomes, list):
                symptomes_txt = ', '.join(
                    EN_TO_FR_SYMPTOM.get(s, s.replace('_', ' ')) for s in symptomes
                ) or '—'
            else:
                symptomes_txt = symptomes or '—'

            lines = [
                f"📋 *Compte rendu du {date_str}*\n",
                f"👨‍⚕️ Dr. {consultation.medecin.get_full_name()}",
            ]
            if consultation.diagnostic:
                lines.append(f"✅ *Diagnostic :* {consultation.diagnostic}")
            if symptomes_txt and symptomes_txt != '—':
                lines.append(f"🔍 *Symptômes :* {symptomes_txt}")
            if consultation.suggestions_ia:
                sug = consultation.suggestions_ia
                if isinstance(sug, list) and sug:
                    top = sug[0]
                    d = top.get('disease', '')
                    d_fr = EN_TO_FR_DISEASE.get(d) or EN_TO_FR_DISEASE.get(d.lower()) or d
                    lines.append(f"🤖 *IA :* {d_fr} ({top.get('confidence', '')}%)")
            try:
                if hasattr(consultation, 'prescription') and consultation.prescription:
                    lines.append("\n💊 _Tapez *mon ordonnance* pour recevoir votre ordonnance._")
            except Exception:
                pass

            return "\n".join(lines)

        except Exception as e:
            logger.error("[WhatsApp] Envoi consultation PDF: %s", e)
            # Fallback texte si le PDF échoue
            date_str = consultation.date_consultation.strftime('%d/%m/%Y')
            return (
                f"📋 *Consultation du {date_str}*\n"
                f"👨‍⚕️ Dr. {consultation.medecin.get_full_name()}\n"
                f"✅ Diagnostic : {consultation.diagnostic or '—'}\n\n"
                "⚠️ _Le PDF n'a pas pu être envoyé. Contactez la clinique._"
            )

    # ═══════════════════════════════════════════════════════════════════════════
    # ANALYSE DE SYMPTÔMES
    # ═══════════════════════════════════════════════════════════════════════════

    def _symptoms(self, message: str) -> str:
        try:
            r = requests.post(
                f"{settings.IA_SERVICE_URL}/brain",
                json={
                    'message': message,
                    'context': 'Patient WhatsApp CuraMedical',
                    'audience': 'patient',
                },
                timeout=12,
            )
            if r.ok:
                data = r.json()
                if data.get('intent') == 'ia_symptoms' and data.get('symptoms'):
                    return self._diagnose(data['symptoms'])
                return data.get('reply') or data.get('response') or self._default_reply()
        except Exception as e:
            logger.error("[WhatsApp] IA brain error: %s", e)
        return self._default_reply()

    def _diagnose(self, symptoms: list) -> str:
        symptoms_fr = [EN_TO_FR_SYMPTOM.get(s, s) for s in symptoms]
        RISK = {'eleve': '🔴', 'modere': '🟡', 'faible': '🟢'}
        try:
            r = requests.post(
                f"{settings.IA_SERVICE_URL}/predict",
                json={'symptoms': symptoms},
                timeout=10,
            )
            if r.ok:
                suggestions = r.json().get('suggestions', [])
                if suggestions:
                    lines = [f"🔬 *Analyse — {', '.join(symptoms_fr)}*\n"]
                    for s in suggestions[:3]:
                        icon = RISK.get(s.get('risk_level', ''), '⚪')
                        d = s['disease']
                        disease_fr = EN_TO_FR_DISEASE.get(d) or EN_TO_FR_DISEASE.get(d.lower()) or EN_TO_FR_DISEASE.get(d.title()) or d
                        lines.append(f"{icon} {disease_fr} — {s['confidence']:.0f}%")
                    lines += [
                        "",
                        "⚠️ *Résultat indicatif uniquement.*",
                        "Consultez un médecin pour un diagnostic précis.",
                        "",
                        "📅 Tapez *rendez-vous* pour prendre un RDV.",
                    ]
                    return "\n".join(lines)
        except Exception as e:
            logger.error("[WhatsApp] /predict error: %s", e)

        return (
            f"🔬 Symptômes : {', '.join(symptoms_fr)}\n\n"
            "Consultez un médecin pour un diagnostic précis.\n"
            "📅 Tapez *rendez-vous* pour prendre un RDV."
        )

    def _default_reply(self) -> str:
        return (
            "Je n'ai pas bien compris.\n\n"
            + self._menu_body()
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # CERVEAU LLM — LLaMA 3.3 70B via Groq
    # ═══════════════════════════════════════════════════════════════════════════

    def _llm_understand(self, message: str, state: str = IDLE) -> dict:
        """Appelle LLaMA pour comprendre l'intention et extraire les entités."""
        if not settings.GROQ_API_KEY:
            return {'intent': 'autre', 'reply': self._default_reply()}
        try:
            from groq import Groq
            patient_name = f"{self.patient.prenom} {self.patient.nom}" if self.patient else "non identifié"

            state_labels = {
                BOOKING_DATE:    "en attente de la DATE du rendez-vous",
                BOOKING_TIME:    "en attente de l'HEURE du rendez-vous",
                BOOKING_MOTIF:   "en attente du MOTIF du rendez-vous",
                BOOKING_TYPE:    "en attente du TYPE (cabinet ou téléconsultation)",
                BOOKING_CONFIRM: "en attente de la CONFIRMATION (oui/non)",
                CHOOSE_ORDONNANCE: "en attente du CHOIX de l'ordonnance (numéro)",
            }
            state_ctx = ""
            if state != IDLE:
                state_ctx = f"\nContexte actuel : {state_labels.get(state, state)}. Si le message répond à cette question, retourne intent=oui ou intent=autre. Si le message demande clairement autre chose (ordonnance, consultation, ses rdv...), retourne l'intent correspondant."

            system = _LLM_SYSTEM.format(
                today=datetime.now().strftime('%A %d %B %Y'),
                patient=patient_name,
            ) + state_ctx
            client = Groq(api_key=settings.GROQ_API_KEY)
            resp = client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user',   'content': message},
                ],
                response_format={'type': 'json_object'},
                temperature=0.1,
                max_tokens=400,
            )
            result = json.loads(resp.choices[0].message.content)
            logger.debug("[LLM] raw=%s", str(result)[:150])
            return result
        except Exception as exc:
            logger.error("[LLM] Erreur : %s", exc)
            return {'intent': 'autre', 'reply': None}

    def _symptoms_llm(self, llm: dict) -> str | None:
        """Utilise les symptômes extraits par le LLM pour le diagnostic IA."""
        symptoms = llm.get('symptoms') or []
        if symptoms:
            return self._diagnose(symptoms)
        return None

    # ── Prise de RDV intelligente ─────────────────────────────────────────────

    def _start_booking_smart(self, msg: str, llm: dict) -> str:
        """Démarre la prise de RDV en pré-remplissant les champs extraits par le LLM."""
        rd = llm.get('rdv_data') or {}
        data = {**self.conv.state_data}

        # Pré-remplissage depuis le LLM
        if rd.get('date'):
            try:
                dt = datetime.fromisoformat(rd['date'])
                data['date'] = rd['date']
                data['date_label'] = self._format_date(dt)
            except Exception:
                pass
        if rd.get('heure') is not None:
            data['heure'] = rd['heure']
            data['heure_label'] = f"{rd['heure']}h"
        if rd.get('motif'):
            data['motif'] = rd['motif']
        if rd.get('type') in ('PRESENTIEL', 'EN_LIGNE'):
            data['type_consultation'] = rd['type']
            data['type_label'] = '🏥 Cabinet' if rd['type'] == 'PRESENTIEL' else '📹 Téléconsultation'

        # Aller directement à l'étape manquante
        if not data.get('date'):
            self._set_state(BOOKING_DATE, data)
            return "🗓️ *Prise de rendez-vous*\n\nPour quelle *date* ?\n_Ex : demain, lundi, 25/05_"
        if data.get('heure') is None:
            self._set_state(BOOKING_TIME, data)
            return f"✅ Date : *{data['date_label']}*\n\nÀ quelle *heure* ?\n_Ex : 9h, 14h30, matin_"
        if not data.get('motif'):
            self._set_state(BOOKING_MOTIF, data)
            return "Quel est le *motif* de votre visite ?"
        if not data.get('type_consultation'):
            self._set_state(BOOKING_TYPE, data)
            return "Quel type ?\n\n*1* 🏥 Cabinet  /  *2* 📹 Téléconsultation"

        # Tout est rempli → récap + confirmation
        self._set_state(BOOKING_CONFIRM, data)
        return self._recap_rdv(data)

    def _booking_date_smart(self, msg: str, llm: dict) -> str:
        """Gère l'étape date avec extraction LLM."""
        rd = llm.get('rdv_data') or {}
        if rd.get('date'):
            try:
                dt = datetime.fromisoformat(rd['date'])
                label = self._format_date(dt)
                # Partir du state_data existant (preserve rdv_id, motif, type pré-remplis)
                data = {**self.conv.state_data, 'date': rd['date'], 'date_label': label}
                # Enrichir avec les entités extraites du message courant
                if rd.get('heure') is not None:
                    data['heure'] = rd['heure']
                    data['heure_label'] = f"{rd['heure']}h"
                if rd.get('motif'):
                    data['motif'] = rd['motif']
                if rd.get('type') in ('PRESENTIEL', 'EN_LIGNE'):
                    data['type_consultation'] = rd['type']
                    data['type_label'] = '🏥 Cabinet' if rd['type'] == 'PRESENTIEL' else '📹 Téléconsultation'
                # Naviguer vers l'étape manquante (vérifie data, pas seulement rd)
                if data.get('heure') is None:
                    self._set_state(BOOKING_TIME, data)
                    return f"✅ Date : *{label}*\n\nÀ quelle *heure* ?\n_Ex : 9h, 14h30, matin_"
                if not data.get('motif'):
                    self._set_state(BOOKING_MOTIF, data)
                    return "Quel est le *motif* de votre visite ?"
                if not data.get('type_consultation'):
                    self._set_state(BOOKING_TYPE, data)
                    return "Quel type ?\n\n*1* 🏥 Cabinet  /  *2* 📹 Téléconsultation"
                self._set_state(BOOKING_CONFIRM, data)
                return self._recap_rdv(data)
            except Exception:
                pass
        return self._booking_date(msg)

    def _booking_time_smart(self, msg: str, llm: dict) -> str:
        """Gère l'étape heure avec extraction LLM."""
        rd = llm.get('rdv_data') or {}
        if rd.get('heure') is not None:
            data = {**self.conv.state_data, 'heure': rd['heure'], 'heure_label': f"{rd['heure']}h"}
            if rd.get('motif'):
                data['motif'] = rd['motif']
            if rd.get('type') in ('PRESENTIEL', 'EN_LIGNE'):
                data['type_consultation'] = rd['type']
                data['type_label'] = '🏥 Cabinet' if rd['type'] == 'PRESENTIEL' else '📹 Téléconsultation'
            if not data.get('motif'):
                self._set_state(BOOKING_MOTIF, data)
                return "Quel est le *motif* de votre visite ?"
            if not data.get('type_consultation'):
                self._set_state(BOOKING_TYPE, data)
                return "Quel type ?\n\n*1* 🏥 Cabinet  /  *2* 📹 Téléconsultation"
            self._set_state(BOOKING_CONFIRM, data)
            return self._recap_rdv(data)
        return self._booking_time(msg)

    def _recap_rdv(self, data: dict) -> str:
        return (
            f"📋 *Récapitulatif :*\n\n"
            f"📅 Date  : {data.get('date_label', '—')}\n"
            f"⏰ Heure : {data.get('heure_label', '—')}\n"
            f"🩺 Motif : {data.get('motif', '—')}\n"
            f"🏥 Type  : {data.get('type_label', '—')}\n\n"
            "Confirmez-vous ? Répondez *oui* ou *non*."
        )

    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITAIRES
    # ═══════════════════════════════════════════════════════════════════════════

    def _set_state(self, state: str, data: dict):
        self.conv.state = state
        self.conv.state_data = data
        self.conv.save(update_fields=['state', 'state_data', 'updated_at'])

    def _not_registered(self) -> str:
        return (
            "⚠️ Votre numéro n'est pas associé à un dossier patient.\n\n"
            "Contactez la clinique pour vous enregistrer :\n"
            "📞 +212 5 22 00 00 00\n"
            "🏥 Clinique CuraMedical"
        )

    # ── Parsing date ──────────────────────────────────────────────────────────

    def _parse_date(self, text: str):
        text = text.lower().strip()
        today = date.today()

        if any(w in text for w in ["aujourd'hui", 'ce soir', 'maintenant']):
            return datetime.combine(today, datetime.min.time())
        if 'demain' in text:
            return datetime.combine(today + timedelta(days=1), datetime.min.time())
        if 'après-demain' in text or 'apres-demain' in text:
            return datetime.combine(today + timedelta(days=2), datetime.min.time())

        m = re.search(r'dans\s+(\d+)\s+jour', text)
        if m:
            return datetime.combine(today + timedelta(days=int(m.group(1))), datetime.min.time())

        DAYS = {
            'lundi': 0, 'mardi': 1, 'mercredi': 2, 'jeudi': 3,
            'vendredi': 4, 'samedi': 5, 'dimanche': 6,
        }
        for name, num in DAYS.items():
            if name in text:
                delta = (num - today.weekday()) % 7 or 7
                return datetime.combine(today + timedelta(days=delta), datetime.min.time())

        m = re.search(r'(\d{1,2})[/\-\.](\d{1,2})(?:[/\-\.](\d{4}))?', text)
        if m:
            day, month = int(m.group(1)), int(m.group(2))
            year = int(m.group(3)) if m.group(3) else today.year
            try:
                return datetime(year, month, day)
            except ValueError:
                pass

        # "le 25" → 25 du mois courant ou suivant
        m = re.search(r'le\s+(\d{1,2})', text)
        if m:
            day = int(m.group(1))
            try:
                d = date(today.year, today.month, day)
                if d < today:
                    # Mois suivant
                    if today.month == 12:
                        d = date(today.year + 1, 1, day)
                    else:
                        d = date(today.year, today.month + 1, day)
                return datetime.combine(d, datetime.min.time())
            except ValueError:
                pass
        return None

    def _parse_time(self, text: str) -> int:
        text = text.lower().strip()
        if 'matin' in text:
            return 9
        if any(w in text for w in ['après-midi', 'apres-midi', 'après midi']):
            return 14
        if 'midi' in text:
            return 12
        if 'soir' in text:
            return 17
        m = re.search(r'(\d{1,2})h?(?:[:\s](\d{2}))?', text)
        if m:
            return int(m.group(1))
        return 9

    @staticmethod
    def _to_casablanca(dt) -> datetime:
        """Convertit n'importe quel datetime en heure locale Casablanca."""
        from zoneinfo import ZoneInfo
        tz_casa = ZoneInfo('Africa/Casablanca')
        if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
            return dt.astimezone(tz_casa)
        # datetime naïf : on suppose qu'il est déjà en heure locale
        return dt

    def _format_date(self, dt) -> str:
        MONTHS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                  'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        DAYS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
        local = self._to_casablanca(dt) if isinstance(dt, datetime) else dt
        d = local.date() if isinstance(local, datetime) else local
        return f"{DAYS[d.weekday()]} {d.day} {MONTHS[d.month - 1]} {d.year}"

    def _format_datetime(self, dt) -> str:
        local = self._to_casablanca(dt)
        return f"{self._format_date(local)} à {local.strftime('%Hh%M')}"
