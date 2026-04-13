import re
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def normalize(text):
    """Normalise le texte pour la recherche."""
    text = text.lower().strip()
    # Supprimer les accents courants
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ç': 'c',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def match(text, *keyword_groups):
    """Retourne True si le texte contient au moins un mot-clé de chaque groupe."""
    t = normalize(text)
    for group in keyword_groups:
        if not any(kw in t for kw in group):
            return False
    return True


def match_any(text, keywords):
    """Retourne True si le texte contient au moins un mot-clé."""
    t = normalize(text)
    return any(kw in t for kw in keywords)


def extract_name(text):
    """Essaye d'extraire un nom propre du message."""
    # Patterns courants
    patterns = [
        r"(?:informations?|info|infos|details?|dossier|fiche|profil)\s+(?:sur|de|du|d')\s+(.+)",
        r"(?:cherche|recherche|trouve|trouver)\s+(?:le\s+patient\s+)?(.+)",
        r"(?:qui\s+est|c'est\s+qui)\s+(.+)",
        r"patient\s+(.+)",
        r"(?:montre|affiche|voir)\s+(?:le\s+dossier\s+(?:de|du)\s+)?(.+)",
    ]
    for pattern in patterns:
        m = re.search(pattern, text.lower().strip().rstrip('?!.'))
        if m:
            name = m.group(1).strip()
            # Nettoyer les mots parasites
            for stop in ['s\'il vous plait', 'svp', 'stp', 'please', 'merci']:
                name = name.replace(stop, '').strip()
            if len(name) >= 2:
                return name
    return None


# ─────────────────────────────────────────────────────────────
# Intent handlers
# ─────────────────────────────────────────────────────────────

def handle_greetings(user, message):
    """Salutations."""
    greetings = ['bonjour', 'salut', 'hello', 'hey', 'bonsoir', 'coucou', 'hi', 'yo', 'salam']
    if match_any(message, greetings):
        name = user.first_name or user.username
        hour = timezone.now().hour
        if hour < 12:
            period = "Bonjour"
        elif hour < 18:
            period = "Bon après-midi"
        else:
            period = "Bonsoir"
        return (
            f"{period}, **{name}** ! 👋\n\n"
            f"Je suis l'assistant IA de MedPredict. Voici ce que je peux faire :\n\n"
            f"• 🩺 Analyser des **symptômes** via l'IA\n"
            f"• 👥 Rechercher un **patient** par nom\n"
            f"• 📅 Consulter les prochains **rendez-vous**\n"
            f"• 💊 Informations sur les **ordonnances**\n"
            f"• 📋 Aide pour les **consultations**\n"
            f"• 🏥 **Statistiques** du cabinet\n"
            f"• ❓ **Comment faire** pour créer un patient, un RDV, etc.\n\n"
            f"Posez-moi simplement votre question ! 😊"
        )
    return None


def handle_thanks(user, message):
    """Remerciements."""
    thanks = ['merci', 'thanks', 'thank you', 'cool', 'parfait', 'genial', 'super', 'top', 'excellent', 'nickel']
    if match_any(message, thanks):
        return f"Avec plaisir, **{user.first_name or user.username}** ! 😊 N'hésitez pas si vous avez d'autres questions."
    return None


def handle_goodbye(user, message):
    """Au revoir."""
    byes = ['au revoir', 'bye', 'a bientot', 'a plus', 'bonne journee', 'bonne soiree', 'ciao', 'a demain']
    if match_any(message, byes):
        return f"À bientôt, **{user.first_name or user.username}** ! 👋 Bonne continuation."
    return None


def handle_identity(user, message):
    """Questions sur l'identité du bot."""
    identity_kw = ['qui es-tu', 'qui es tu', 'tu es qui', 'c\'est quoi', 'quel est ton', 'ton nom',
                   'comment tu t\'appelles', 'tu t appelles', 'what are you', 'qui etes-vous',
                   'presente-toi', 'presente toi', 'tu fais quoi', 'a quoi tu sers']
    if match_any(message, identity_kw):
        return (
            "🤖 Je suis l'**Assistant IA de MedPredict**, votre compagnon médical intelligent !\n\n"
            "Je peux :\n"
            "• Rechercher des **patients** par nom et afficher leurs informations\n"
            "• Consulter les **rendez-vous** à venir\n"
            "• Analyser des **symptômes** via notre modèle d'IA\n"
            "• Donner des **statistiques** sur l'activité du cabinet\n"
            "• Vous guider dans l'utilisation de l'application\n\n"
            "Demandez-moi ce que vous voulez ! 💡"
        )
    return None


def handle_help(user, message):
    """Aide générale."""
    help_kw = ['aide', 'help', 'comment faire', 'fonctionnalites', 'quoi faire', 'que peux-tu',
               'que peux tu', 'que sais-tu', 'que sais tu', 'capabilities', 'options',
               'menu', 'commandes', 'liste', 'guide']
    if match_any(message, help_kw):
        return (
            "🏥 **Guide complet de l'Assistant MedPredict :**\n\n"
            "**📋 Recherche & Informations :**\n"
            "• \"Informations sur Jean Dupont\"\n"
            "• \"Liste des patients\"\n"
            "• \"Prochains rendez-vous\"\n"
            "• \"Statistiques du cabinet\"\n\n"
            "**🩺 Intelligence Artificielle :**\n"
            "• \"Quels symptômes analyser ?\"\n"
            "• \"Analyse fièvre et toux\"\n\n"
            "**📝 Comment faire :**\n"
            "• \"Comment créer un patient ?\"\n"
            "• \"Comment prendre un rendez-vous ?\"\n"
            "• \"Comment créer une ordonnance ?\"\n"
            "• \"Comment faire une consultation ?\"\n\n"
            "**💡 Autres :**\n"
            "• \"Rendez-vous d'aujourd'hui\"\n"
            "• \"Combien de patients actifs ?\"\n"
            "• \"Dernières consultations\"\n"
        )
    return None


def handle_how_to_patient(user, message):
    """Comment créer/gérer un patient."""
    if match(message, ['comment', 'creer', 'ajouter', 'nouveau', 'enregistrer', 'inscrire'], ['patient']):
        return (
            "📝 **Comment créer un nouveau patient :**\n\n"
            "1. Cliquez sur **Patients** dans le menu de gauche\n"
            "2. Cliquez sur le bouton **+ Nouveau patient** en haut à droite\n"
            "3. Remplissez le formulaire :\n"
            "   • **Prénom** et **Nom** (obligatoires)\n"
            "   • **Date de naissance** (obligatoire)\n"
            "   • **CIN** (obligatoire)\n"
            "   • **Genre**, **Téléphone**, **Email**\n"
            "   • **Groupe sanguin**, **Allergies**, **Antécédents médicaux**\n"
            "4. Cliquez sur **Enregistrer**\n\n"
            "💡 Le patient apparaîtra immédiatement dans la liste !"
        )
    return None


def handle_how_to_appointment(user, message):
    """Comment créer un RDV."""
    if match(message, ['comment', 'creer', 'prendre', 'ajouter', 'planifier', 'nouveau'], ['rdv', 'rendez-vous', 'rendez vous', 'appointment']):
        return (
            "📅 **Comment planifier un rendez-vous :**\n\n"
            "1. Cliquez sur **Rendez-vous** dans le menu de gauche\n"
            "2. Cliquez sur **+ Nouveau rendez-vous**\n"
            "3. Remplissez :\n"
            "   • Sélectionnez le **Patient**\n"
            "   • Sélectionnez le **Médecin**\n"
            "   • Choisissez la **Date et heure**\n"
            "   • Indiquez la **Durée** (15-120 min)\n"
            "   • Précisez le **Motif** de consultation\n"
            "4. Cliquez sur **Enregistrer**\n\n"
            "💡 Vous pouvez changer le statut (Planifié → Confirmé → En cours → Terminé) directement depuis la liste."
        )
    return None


def handle_how_to_consultation(user, message):
    """Comment créer une consultation."""
    if match(message, ['comment', 'creer', 'faire', 'ajouter', 'nouvelle'], ['consultation']):
        return (
            "🩺 **Comment créer une consultation :**\n\n"
            "1. Cliquez sur **Consultations** dans le menu de gauche\n"
            "2. Cliquez sur **+ Nouvelle consultation**\n"
            "3. Étapes :\n"
            "   • Sélectionnez le **rendez-vous associé**\n"
            "   • Cochez les **symptômes** observés\n"
            "   • *(Optionnel)* Cliquez sur **🔍 Analyser les symptômes** pour obtenir une prédiction IA\n"
            "   • Rédigez l'**examen clinique**\n"
            "   • Indiquez le **diagnostic retenu**\n"
            "   • Ajoutez des **notes** si nécessaire\n"
            "4. Cliquez sur **Enregistrer la consultation**\n\n"
            "💡 Vous pouvez cliquer sur une suggestion IA pour l'utiliser directement comme diagnostic !"
        )
    return None


def handle_how_to_prescription(user, message):
    """Comment créer une ordonnance."""
    if match(message, ['comment', 'creer', 'faire', 'ajouter', 'nouvelle', 'rediger'], ['ordonnance', 'prescription']):
        return (
            "💊 **Comment créer une ordonnance :**\n\n"
            "1. Cliquez sur **Ordonnances** dans le menu de gauche\n"
            "2. Cliquez sur **+ Nouvelle ordonnance**\n"
            "3. Étapes :\n"
            "   • Sélectionnez la **consultation associée**\n"
            "   • Pour chaque médicament, renseignez :\n"
            "     - **Nom du médicament** (ex: Amoxicilline)\n"
            "     - **Dosage** (ex: 500mg)\n"
            "     - **Posologie** (ex: 3 fois par jour)\n"
            "     - **Durée** (ex: 7 jours)\n"
            "     - **Instructions spéciales** (optionnel)\n"
            "   • Cliquez sur **Ajouter un médicament** pour en ajouter d'autres\n"
            "   • Ajoutez des **instructions générales** si nécessaire\n"
            "4. Cliquez sur **Créer l'ordonnance**\n\n"
            "💡 Vous pouvez ensuite **télécharger le PDF** de l'ordonnance !"
        )
    return None


def handle_patient_search(user, message):
    """Recherche d'un patient par nom. Réservé au staff."""
    if user.role == 'patient':
        return "⚠️ En tant que patient, vous n'êtes pas autorisé à rechercher d'autres dossiers médicaux."
    
    name = extract_name(message)
    if not name:
        # Vérifier les patterns alternatifs
        info_kw = ['informations', 'information', 'info', 'infos', 'details', 'detail',
                    'dossier', 'fiche', 'profil', 'cherche', 'recherche', 'trouve',
                    'trouver', 'montre', 'affiche', 'voir']
        if not match_any(message, info_kw):
            return None
        # Essayer d'extraire le nom autrement
        words = message.strip().rstrip('?!.').split()
        # Prendre les mots qui commencent par une majuscule (noms propres potentiels)
        proper_nouns = [w for w in words if w[0].isupper() and len(w) > 1 and w.lower() not in
                        ['je', 'tu', 'il', 'elle', 'nous', 'vous', 'les', 'des', 'une', 'quels',
                         'quelle', 'quel', 'mon', 'ton', 'son', 'cette', 'comment', 'pourquoi',
                         'donne', 'toutes', 'sur', 'pour']]
        if proper_nouns:
            name = ' '.join(proper_nouns)
        else:
            return None

    from apps.patients.models import Patient

    # Recherche flexible
    query_parts = name.split()
    q = Q()
    for part in query_parts:
        q &= (
            Q(first_name__icontains=part) |
            Q(last_name__icontains=part) |
            Q(national_id__icontains=part)
        )

    patients = Patient.objects.filter(q, is_archived=False)[:5]

    if not patients.exists():
        # Essayer une recherche plus large
        q_loose = Q()
        for part in query_parts:
            q_loose |= (
                Q(first_name__icontains=part) |
                Q(last_name__icontains=part)
            )
        patients = Patient.objects.filter(q_loose, is_archived=False)[:5]

    if not patients.exists():
        return (
            f"🔍 Aucun patient trouvé pour **\"{name}\"**.\n\n"
            f"Vérifiez l'orthographe ou essayez avec moins de lettres.\n"
            f"Vous pouvez aussi consulter la liste complète dans l'onglet **Patients**."
        )

    if patients.count() == 1:
        p = patients.first()
        lines = [f"👤 **Fiche patient : {p.first_name} {p.last_name}**\n"]
        fields = [
            ("CIN", p.national_id),
            ("Date de naissance", p.date_of_birth),
            ("Âge", f"{p.age} ans" if hasattr(p, 'age') and p.age else None),
            ("Genre", "Masculin" if p.gender == 'M' else "Féminin"),
            ("Téléphone", p.phone),
            ("Email", p.email),
            ("Adresse", p.address),
            ("Groupe sanguin", p.blood_group),
            ("Allergies", p.allergies),
            ("Antécédents médicaux", p.medical_history),
        ]
        for label, value in fields:
            if value:
                lines.append(f"• **{label}** : {value}")

        # Compter les RDV et consultations
        try:
            from apps.appointments.models import Appointment
            from apps.consultations.models import Consultation
            rdv_count = Appointment.objects.filter(patient=p).count()
            consult_count = Consultation.objects.filter(appointment__patient=p).count()
            lines.append(f"\n📊 **Activité** : {rdv_count} rendez-vous, {consult_count} consultation(s)")
        except Exception:
            pass

        return '\n'.join(lines)
    else:
        lines = [f"🔍 **{patients.count()} patient(s) trouvé(s) pour \"{name}\" :**\n"]
        for p in patients:
            age_str = f", {p.age} ans" if hasattr(p, 'age') and p.age else ""
            lines.append(f"• **{p.first_name} {p.last_name}** — CIN: {p.national_id or '—'}{age_str}")
        lines.append(f"\n💡 Précisez le nom complet pour voir le détail d'un patient.")
        return '\n'.join(lines)


def handle_patient_list(user, message):
    """Liste des patients. Réservé au staff."""
    if user.role == 'patient':
        return "⚠️ Accès refusé : la liste des patients est réservée au personnel médical."

    list_kw = ['liste', 'lister', 'tous les', 'combien', 'nombre', 'total', 'actif', 'actifs', 'enregistre']
    if match(message, list_kw, ['patient']):
        from apps.patients.models import Patient
        total = Patient.objects.filter(is_archived=False).count()
        archived = Patient.objects.filter(is_archived=True).count()
        recent = Patient.objects.filter(is_archived=False).order_by('-created_at')[:5]

        lines = [f"👥 **Statistiques des patients :**\n"]
        lines.append(f"• **{total}** patient(s) actif(s)")
        lines.append(f"• **{archived}** patient(s) archivé(s)")

        if recent.exists():
            lines.append(f"\n📋 **Derniers patients ajoutés :**")
            for p in recent:
                gender = "♂" if p.gender == 'M' else "♀"
                age_str = f", {p.age} ans" if hasattr(p, 'age') and p.age else ""
                lines.append(f"• {gender} **{p.first_name} {p.last_name}**{age_str}")

        lines.append(f"\n💡 Dites *\"info [nom]\"* pour voir le détail d'un patient.")
        return '\n'.join(lines)
    return None


def handle_appointments_upcoming(user, message):
    """Prochains rendez-vous."""
    rdv_kw = ['rdv', 'rendez-vous', 'rendez vous', 'appointment', 'agenda', 'planning']
    upcoming_kw = ['prochain', 'prochains', 'a venir', 'avenir', 'futur', 'planifie', 'prevu', 'prevus']

    if match_any(message, rdv_kw):
        from apps.appointments.models import Appointment

        # Aujourd'hui ?
        today_kw = ['aujourd\'hui', "aujourd'hui", 'aujourdhui', 'today', 'ce jour', 'du jour']
        if match_any(message, today_kw):
            today = timezone.now().date()
            appts = Appointment.objects.filter(
                scheduled_at__date=today
            ).order_by('scheduled_at')[:10]
            if not appts.exists():
                return "📅 **Aucun rendez-vous prévu aujourd'hui.** Profitez-en pour mettre à jour vos dossiers ! 😊"
            lines = [f"📅 **Rendez-vous d'aujourd'hui ({today.strftime('%d/%m/%Y')}) :**\n"]
            for a in appts:
                patient = a.patient.full_name if a.patient else '—'
                doctor = f"Dr. {a.doctor.last_name}" if a.doctor else '—'
                time = a.scheduled_at.strftime('%Hh%M')
                status_map = {'planned': '🟡', 'confirmed': '🔵', 'in_progress': '🟣', 'completed': '✅', 'cancelled': '🔴'}
                icon = status_map.get(a.status, '⚪')
                lines.append(f"• {icon} **{time}** — {patient} avec {doctor} ({a.duration} min)")
            return '\n'.join(lines)

        # Demain ?
        demain_kw = ['demain', 'tomorrow']
        if match_any(message, demain_kw):
            tomorrow = timezone.now().date() + timedelta(days=1)
            appts = Appointment.objects.filter(
                scheduled_at__date=tomorrow
            ).order_by('scheduled_at')[:10]
            if not appts.exists():
                return f"📅 **Aucun rendez-vous prévu pour demain** ({tomorrow.strftime('%d/%m/%Y')})."
            lines = [f"📅 **Rendez-vous de demain ({tomorrow.strftime('%d/%m/%Y')}) :**\n"]
            for a in appts:
                patient = a.patient.full_name if a.patient else '—'
                doctor = f"Dr. {a.doctor.last_name}" if a.doctor else '—'
                time = a.scheduled_at.strftime('%Hh%M')
                lines.append(f"• **{time}** — {patient} avec {doctor} ({a.duration} min)")
            return '\n'.join(lines)

        # Cette semaine ?
        semaine_kw = ['semaine', 'cette semaine', 'week']
        if match_any(message, semaine_kw):
            start = timezone.now().date()
            end = start + timedelta(days=7)
            appts = Appointment.objects.filter(
                scheduled_at__date__range=[start, end]
            ).order_by('scheduled_at')[:15]
            if not appts.exists():
                return "📅 **Aucun rendez-vous prévu cette semaine.**"
            lines = [f"📅 **Rendez-vous de la semaine :**\n"]
            for a in appts:
                patient = a.patient.full_name if a.patient else '—'
                dt = a.scheduled_at.strftime('%d/%m %Hh%M')
                lines.append(f"• **{dt}** — {patient} ({a.get_status_display()})")
            return '\n'.join(lines)

        # Prochains par défaut
        appts = Appointment.objects.filter(
            status__in=['planned', 'confirmed']
        ).order_by('scheduled_at')[:8]

        if not appts.exists():
            return "📅 **Aucun rendez-vous planifié pour le moment.**\n\nVoulez-vous en créer un ?"

        lines = [f"📅 **Prochains rendez-vous :**\n"]
        for a in appts:
            patient = a.patient.full_name if a.patient else '—'
            doctor = f"Dr. {a.doctor.last_name}" if a.doctor else '—'
            dt = a.scheduled_at.strftime('%d/%m/%Y %Hh%M')
            status_map = {'planned': 'Planifié', 'confirmed': 'Confirmé'}
            status = status_map.get(a.status, a.status)
            lines.append(f"• **{patient}** avec {doctor}\n  📆 {dt} — _{status}_")
        lines.append(f"\n💡 Dites *\"RDV aujourd'hui\"* ou *\"RDV demain\"* pour filtrer.")
        return '\n'.join(lines)

    return None


def handle_consultation_info(user, message):
    """Informations sur les consultations."""
    consult_kw = ['consultation', 'consultations', 'diagnostic', 'diagnostics']
    if match_any(message, consult_kw):
        from apps.consultations.models import Consultation

        # Dernières consultations
        dernier_kw = ['derniere', 'dernieres', 'derniers', 'recente', 'recentes', 'recent', 'historique']
        if match_any(message, dernier_kw) or match(message, ['liste', 'lister', 'combien', 'nombre', 'total'], consult_kw):
            total = Consultation.objects.count()
            ia_count = Consultation.objects.filter(ia_used=True).count()
            recent = Consultation.objects.order_by('-created_at')[:5]

            lines = [f"📋 **Statistiques des consultations :**\n"]
            lines.append(f"• **{total}** consultation(s) au total")
            lines.append(f"• **{ia_count}** avec assistance IA ({round(ia_count/max(total,1)*100)}%)")

            if recent.exists():
                lines.append(f"\n🕐 **Dernières consultations :**")
                for c in recent:
                    patient = c.patient_name or '—'
                    date = c.created_at.strftime('%d/%m/%Y')
                    ia = "🤖" if c.ia_used else ""
                    lines.append(f"• {ia} **{patient}** — {c.diagnosis or '—'} ({date})")

            return '\n'.join(lines)

        # Instructions par défaut
        return (
            "📋 **Consultations — Aide :**\n\n"
            "Pour créer une consultation :\n"
            "1. Allez dans **Consultations** → **+ Nouvelle consultation**\n"
            "2. Sélectionnez le rendez-vous, cochez les symptômes\n"
            "3. Utilisez l'**IA** pour obtenir des suggestions de diagnostic\n"
            "4. Rédigez votre diagnostic et vos notes\n\n"
            "💡 Dites *\"dernières consultations\"* pour voir l'historique."
        )
    return None


def handle_prescription_info(user, message):
    """Informations sur les ordonnances."""
    rx_kw = ['ordonnance', 'ordonnances', 'prescription', 'prescriptions', 'medicament', 'medicaments',
             'traitement', 'traitements', 'posologie']
    if match_any(message, rx_kw):
        from apps.prescriptions.models import Prescription

        total = Prescription.objects.count()
        recent = Prescription.objects.order_by('-created_at')[:5]

        lines = [f"💊 **Ordonnances — {total} enregistrée(s) :**\n"]

        if recent.exists():
            for p in recent:
                patient = p.patient_name or '—'
                date = p.created_at.strftime('%d/%m/%Y')
                meds = ', '.join([i.medication for i in p.items.all()[:3]]) if hasattr(p, 'items') else '—'
                lines.append(f"• **{patient}** ({date}) : {meds}")
        else:
            lines.append("Aucune ordonnance enregistrée pour le moment.")

        lines.append(f"\n💡 Dites *\"comment créer une ordonnance\"* pour un guide étape par étape.")
        lines.append(f"💡 Vous pouvez **télécharger le PDF** de chaque ordonnance depuis la liste.")
        return '\n'.join(lines)
    return None


def handle_symptoms_ia(user, message, prefilled_symptoms=None):
    """Analyse les symptômes via l'IA étendue (377 symptômes)."""
    normalized = normalize(message)
    ia_kw = ['symptome', 'symptomes', 'ia', 'intelligence artificielle', 'prediction',
             'predire', 'analyse', 'analyser', 'maladie', 'diagnostic ia', 'diagnostic']

    # 1. Recuperation de la liste des symptomes supportes par le service IA
    try:
        r_list = requests.get(f"{settings.IA_SERVICE_URL}/symptoms", timeout=3)
        known_symptoms = r_list.json().get('symptoms', [])
    except Exception:
        known_symptoms = []

    # 2. Extraction dynamique des symptomes presents dans le message
    found_symptoms = prefilled_symptoms if prefilled_symptoms else []
    if not found_symptoms and known_symptoms:
        # On trie par longueur decroissante pour eviter les collisions (ex: "douleur" vs "douleur abdominale")
        for sym in sorted(known_symptoms, key=len, reverse=True):
            if sym.lower() in normalized:
                found_symptoms.append(sym)
                # Optionnel: on peut retirer le symptome du message pour eviter les doublons
                # normalized = normalized.replace(sym.lower(), "")

    # 3. Si des symptomes sont trouves, on lance la prediction
    if found_symptoms:
        try:
            r = requests.post(f"{settings.IA_SERVICE_URL}/predict", json={
                'symptoms': found_symptoms,
            }, timeout=8)
            data = r.json()
            suggestions = data.get('suggestions', [])
            
            if suggestions:
                lines = [f"🧠 **Analyse IA des symptômes détectés :**\n_(Symptômes reconnus : {', '.join(found_symptoms)})_\n"]
                for i, s in enumerate(suggestions[:5]): # Top 5
                    conf = s['confidence']
                    # Gestion spéciale pour les cas indéterminés (score 0)
                    if conf == 0:
                        lines.append(f"⚠️ **{s['disease']}**")
                        lines.append(f"   _{s['explanation']}_")
                        continue

                    # Confidence bar plus élégante
                    filled = int(conf / 10)
                    bar = '●' * filled + '○' * (10 - filled)
                    
                    risk_colors = {'eleve': '🔴', 'modere': '🟠', 'faible': '🟢'}
                    icon = risk_colors.get(s['risk_level'], '⚪')
                    
                    lines.append(f"{i+1}. {icon} **{s['disease']}** — **{conf}%**")
                    lines.append(f"   `{bar}`")
                    if i == 0: # Explication détaillée
                        lines.append(f"   _{s['explanation']}_")
                
                lines.append(f"\n⚠️ _Outil d'aide au diagnostic clinique. Ne remplace pas l'expertise médicale._")
                return '\n'.join(lines)
            else:
                return f"Désolé, je reconnais les symptômes ({', '.join(found_symptoms)}), mais mon modèle IA actuel n'arrive pas à isoler une pathologie de façon probante. 🤔"
        except Exception as e:
            return "⚠️ Désolé, le service d'analyse prédictive est momentanément indisponible."

    # 4. Fallback : Si l'utilisateur pose une question mais sans symptomes clairs
    if match_any(message, ia_kw):
        return (
            "🩺 **Assistant de Diagnostic IA**\n\n"
            "Je peux analyser plus de **770 maladies** à partir de **370+ symptômes**.\n\n"
            "**Comment faire ?**\n"
            "Décrivez simplement vos symptômes, par exemple :\n"
            "_\"J'ai de la fièvre et des douleurs abdominales\"_ ou _\"Analyse toux et fatigue\"_.\n\n"
            "💡 _Note : Plus vous donnez de symptômes précis, plus la prédiction sera fiable._"
        )

    return None


def handle_analyze_appointment(user, partial_name, ai_response=None):
    """Analyse directement le motif médical du rendez-vous d'un patient via Llama 3."""
    from apps.appointments.models import Appointment
    from django.db.models import Q
    from django.conf import settings
    import requests

    q = Q(patient__first_name__icontains=partial_name) | Q(patient__last_name__icontains=partial_name)
    appts = Appointment.objects.filter(q, status__in=['planned', 'confirmed']).order_by('-scheduled_at')
    
    if not appts.exists():
        appts = Appointment.objects.filter(q).order_by('-scheduled_at')

    if not appts.exists():
        return f"Je n'ai pas trouvé de dossier ou de rendez-vous pour **{partial_name}**."

    appt = appts.first()
    reason = appt.reason

    if not reason or len(reason.strip()) < 5:
        return f"Le dernier rendez-vous de **{appt.patient.full_name}** n'a pas de motif suffisamment détaillé."

    intro = f"J'ai examiné le motif du rendez-vous de **{appt.patient.full_name}** :\n_« {reason} »_\n\n"
    
    try:
        # On demande au microservice d'extraire les symptômes via LLM et de prédire
        r = requests.post(f"{settings.IA_SERVICE_URL}/predict", json={'message': reason}, timeout=15)
        data = r.json()
        suggestions = data.get('suggestions', [])
        
        if suggestions:
            lines = [intro, "🧠 **Diagnostic différentiel IA :**"]
            for i, s in enumerate(suggestions[:3]): 
                conf = s['confidence']
                if conf == 0:
                    lines.append(f"⚠️ **{s['disease']}**")
                    lines.append(f"   _{s['explanation']}_")
                    continue

                filled = int(conf / 10)
                bar = '●' * filled + '○' * (10 - filled)
                icon = {'eleve': '🔴', 'modere': '🟠', 'faible': '🟢'}.get(s['risk_level'], '⚪')
                
                lines.append(f"{i+1}. {icon} **{s['disease']}** — **{conf}%**")
                lines.append(f"   `{bar}`")
                if i == 0: lines.append(f"   _{s['explanation']}_")
            
            lines.append(f"\n⚠️ _Ne remplace pas la validation clinique._")
            prefix = f"{ai_response}\n\n" if ai_response else ""
            return f"{prefix}{str.join(chr(10), lines)}"
        else:
            return intro + "Le modèle IA n'a pas pu identifier de signes cliniques exploitables dans ce motif."
    except Exception as e:
        return intro + f"⚠️ Erreur lors de l'analyse IA : {str(e)}"


def handle_stats(user, message):
    """Statistiques du cabinet. Réservé au staff."""
    if user.role == 'patient':
        return "⚠️ Les statistiques globales du cabinet ne sont pas accessibles aux patients."

    stats_kw = ['statistique', 'statistiques', 'stats', 'chiffres', 'resume', 'bilan',
                'tableau de bord', 'dashboard', 'activite', 'rapport', 'overview']
    if match_any(message, stats_kw):
        from apps.patients.models import Patient
        from apps.appointments.models import Appointment
        from apps.consultations.models import Consultation
        from apps.prescriptions.models import Prescription

        patients_count = Patient.objects.filter(is_archived=False).count()
        rdv_count = Appointment.objects.count()
        rdv_today = Appointment.objects.filter(scheduled_at__date=timezone.now().date()).count()
        consultations_count = Consultation.objects.count()
        ia_consultations = Consultation.objects.filter(ia_used=True).count()
        prescriptions_count = Prescription.objects.count()

        return (
            f"📊 **Statistiques du cabinet MedPredict :**\n\n"
            f"👥 **Patients actifs** : {patients_count}\n"
            f"📅 **Rendez-vous** : {rdv_count} au total ({rdv_today} aujourd'hui)\n"
            f"🩺 **Consultations** : {consultations_count} (dont {ia_consultations} avec IA)\n"
            f"💊 **Ordonnances** : {prescriptions_count}\n\n"
            f"📈 _Taux d'utilisation IA : {round(ia_consultations/max(consultations_count,1)*100)}%_"
        )
    return None


def handle_navigation(user, message):
    """Aide à la navigation dans l'application."""
    nav_map = {
        ('ou', 'trouver', 'aller', 'acceder', 'page', 'onglet', 'section', 'naviguer'): {
            'patient': "👥 Pour la page **Patients**, cliquez sur **Patients** dans le menu latéral gauche.",
            'rdv': "📅 Pour les **Rendez-vous**, cliquez sur **Rendez-vous** dans le menu latéral gauche.",
            'rendez-vous': "📅 Pour les **Rendez-vous**, cliquez sur **Rendez-vous** dans le menu latéral gauche.",
            'consultation': "🩺 Pour les **Consultations**, cliquez sur **Consultations** dans le menu latéral gauche.",
            'ordonnance': "💊 Pour les **Ordonnances**, cliquez sur **Ordonnances** dans le menu latéral gauche.",
            'admin': "⚙️ Pour la page **Administration**, cliquez sur **Administration** dans le menu (accès admin uniquement).",
            'dashboard': "📊 Pour le **Tableau de bord**, cliquez sur **Tableau de bord** dans le menu latéral.",
        }
    }
    t = normalize(message)
    for nav_kws, targets in nav_map.items():
        if any(nk in t for nk in nav_kws):
            for target_kw, response_text in targets.items():
                if target_kw in t:
                    return response_text
    return None


def handle_user_info(user, message):
    """Informations sur l'utilisateur connecté."""
    user_kw = ['mon compte', 'mon profil', 'qui suis-je', 'qui suis je', 'mon role',
               'mon nom', 'mes informations', 'mes infos', 'connecte comme']
    if match_any(message, user_kw):
        role_labels = {
            'admin': 'Administrateur',
            'doctor': 'Médecin',
            'secretary': 'Secrétaire',
        }
        role = role_labels.get(user.role, user.role) if hasattr(user, 'role') else '—'
        return (
            f"👤 **Votre profil :**\n\n"
            f"• **Nom** : {user.first_name} {user.last_name}\n"
            f"• **Identifiant** : {user.username}\n"
            f"• **Rôle** : {role}\n"
            f"• **Email** : {user.email or '—'}\n"
        )
    return None


# ─────────────────────────────────────────────────────────────
# Creation flows — multi-turn conversation
# ─────────────────────────────────────────────────────────────

# ── Patient creation steps ──
PATIENT_STEPS = [
    {'key': 'first_name',     'question': "👤 **Création d'un patient — Étape 1/7**\n\nQuel est le **prénom** du patient ?",       'required': True},
    {'key': 'last_name',      'question': "👤 **Étape 2/7**\n\nQuel est le **nom de famille** du patient ?", 'required': True},
    {'key': 'date_of_birth',  'question': "📅 **Étape 3/7**\n\nQuelle est la **date de naissance** ?\n\n_(Format : JJ/MM/AAAA, ex: 15/03/1990)_", 'required': True},
    {'key': 'national_id',    'question': "🪪 **Étape 4/7**\n\nQuel est le **CIN** (numéro d'identité nationale) ?", 'required': True},
    {'key': 'gender',         'question': "⚧ **Étape 5/7**\n\nQuel est le **genre** du patient ?\n\n_(Répondez **M** pour Masculin ou **F** pour Féminin)_", 'required': True},
    {'key': 'phone',          'question': "📱 **Étape 6/7**\n\nQuel est le **numéro de téléphone** ?\n\n_(Tapez **-** pour passer)_", 'required': False},
    {'key': 'email',          'question': "📧 **Étape 7/7**\n\nQuelle est l'**adresse email** ?\n\n_(Tapez **-** pour passer)_", 'required': False},
]

# ── Appointment creation steps ──
APPOINTMENT_STEPS = [
    {'key': 'patient_name',   'question': "📅 **Création d'un RDV — Étape 1/4**\n\nPour quel **patient** ? _(Tapez le nom ou une partie du nom)_", 'required': True},
    {'key': 'scheduled_at',   'question': "🕐 **Étape 2/4**\n\nÀ quelle **date et heure** ?\n\n_(Format : JJ/MM/AAAA HH:MM, ex: 20/03/2026 14:30)_", 'required': True},
    {'key': 'duration',       'question': "⏱️ **Étape 3/4**\n\nQuelle **durée** en minutes ? _(ex: 30)_", 'required': True},
    {'key': 'reason',         'question': "📝 **Étape 4/4**\n\nQuel est le **motif** du rendez-vous ?", 'required': True},
]


def parse_date(text):
    """Parse une date au format JJ/MM/AAAA."""
    text = text.strip().replace('-', '/').replace('.', '/')
    for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d %m %Y']:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def parse_datetime_str(text):
    """Parse une date+heure au format JJ/MM/AAAA HH:MM."""
    text = text.strip().replace('-', '/').replace('.', '/')
    for fmt in ['%d/%m/%Y %H:%M', '%d/%m/%Y %Hh%M', '%Y-%m-%d %H:%M', '%d/%m/%Y %H:%M:%S']:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def validate_patient_field(key, value):
    """Valide un champ patient et retourne (cleaned_value, error_msg)."""
    value = value.strip()

    if value == '-':
        return '', None  # Skip optional field

    if key == 'date_of_birth':
        d = parse_date(value)
        if not d:
            return None, "❌ Format de date invalide. Utilisez **JJ/MM/AAAA** (ex: 15/03/1990)."
        return d.isoformat(), None

    if key == 'gender':
        v = value.upper().strip()
        if v in ('M', 'MASCULIN', 'HOMME', 'H'):
            return 'M', None
        if v in ('F', 'FEMININ', 'FÉMININ', 'FEMME'):
            return 'F', None
        return None, "❌ Répondez **M** (Masculin) ou **F** (Féminin)."

    if key == 'national_id':
        if len(value) < 3:
            return None, "❌ Le CIN semble trop court. Veuillez réessayer."
        return value, None

    if key == 'email' and value:
        if '@' not in value:
            return None, "❌ L'email semble invalide. Tapez **-** pour passer."
        return value, None

    return value, None


def validate_appointment_field(key, value):
    """Valide un champ rendez-vous et retourne (cleaned_value, error_msg)."""
    value = value.strip()

    if key == 'patient_name':
        from apps.patients.models import Patient
        parts = value.split()
        q = Q()
        for part in parts:
            q &= (Q(first_name__icontains=part) | Q(last_name__icontains=part))
        patients = Patient.objects.filter(q, is_archived=False)[:5]

        if not patients.exists():
            # Recherche plus large
            q2 = Q()
            for part in parts:
                q2 |= (Q(first_name__icontains=part) | Q(last_name__icontains=part))
            patients = Patient.objects.filter(q2, is_archived=False)[:5]

        if not patients.exists():
            return None, f"❌ Aucun patient trouvé pour **\"{value}\"**. Vérifiez le nom et réessayez."

        if patients.count() > 1:
            names = '\n'.join([f"• **{p.first_name} {p.last_name}** (CIN: {p.national_id})" for p in patients])
            return None, f"🔍 Plusieurs patients trouvés :\n{names}\n\nPrécisez le nom complet."

        p = patients.first()
        return str(p.id), None

    if key == 'scheduled_at':
        dt = parse_datetime_str(value)
        if not dt:
            return None, "❌ Format invalide. Utilisez **JJ/MM/AAAA HH:MM** (ex: 20/03/2026 14:30)."
        return dt.isoformat(), None

    if key == 'duration':
        try:
            d = int(value)
            if d < 5 or d > 480:
                return None, "❌ La durée doit être entre **5** et **480** minutes."
            return str(d), None
        except ValueError:
            return None, "❌ Veuillez entrer un nombre (ex: **30**)."

    return value, None


def process_creation_flow(user, message, context):
    """Gère un flow de création multi-tour."""
    flow = context.get('flow')
    step_index = context.get('step_index', 0)
    data = context.get('data', {})

    if flow == 'create_patient':
        steps = PATIENT_STEPS
        validate_fn = validate_patient_field
    elif flow == 'create_appointment':
        steps = APPOINTMENT_STEPS
        validate_fn = validate_appointment_field
    else:
        return {'response': "❌ Contexte invalide."}, None

    # Validate current answer
    current_step = steps[step_index]
    cleaned, error = validate_fn(current_step['key'], message)

    if error:
        # Re-ask with error message
        return {
            'response': f"{error}\n\n{current_step['question']}",
            'context': context,
        }, None

    # Store validated value
    data[current_step['key']] = cleaned
    context['data'] = data
    step_index += 1
    context['step_index'] = step_index

    # More steps?
    if step_index < len(steps):
        next_step = steps[step_index]
        context['step'] = step_index + 1
        return {
            'response': next_step['question'],
            'context': context,
        }, None

    # ── All steps done — CREATE ──
    if flow == 'create_patient':
        return _finalize_patient(data)
    elif flow == 'create_appointment':
        return _finalize_appointment(user, data)

    return {'response': "❌ Erreur interne."}, None


def _finalize_patient(data):
    """Crée le patient en base de données."""
    from apps.patients.models import Patient
    try:
        # Check duplicate CIN
        if Patient.objects.filter(national_id=data['national_id']).exists():
            return {
                'response': f"⚠️ Un patient avec le CIN **{data['national_id']}** existe déjà. Opération annulée.",
            }, None

        patient = Patient.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=data['date_of_birth'],
            national_id=data['national_id'],
            gender=data['gender'],
            phone=data.get('phone', ''),
            email=data.get('email', ''),
        )
        gender_label = "Masculin" if patient.gender == 'M' else "Féminin"
        return {
            'response': (
                f"✅ **Patient créé avec succès !**\n\n"
                f"• **Nom** : {patient.first_name} {patient.last_name}\n"
                f"• **CIN** : {patient.national_id}\n"
                f"• **Date de naissance** : {patient.date_of_birth}\n"
                f"• **Genre** : {gender_label}\n"
                f"• **Téléphone** : {patient.phone or '—'}\n"
                f"• **Email** : {patient.email or '—'}\n\n"
                f"🎉 Le patient est maintenant visible dans la liste des patients !"
            ),
            'actions': ['📅 Planifier un RDV', '👤 Ajouter un autre patient'],
        }, None
    except Exception as e:
        return {'response': f"❌ Erreur lors de la création : {str(e)}"}, None


def _finalize_appointment(user, data):
    """Crée le RDV en base de données."""
    from apps.patients.models import Patient
    from apps.appointments.models import Appointment
    from apps.users.models import User

    try:
        patient = Patient.objects.get(id=int(data['patient_name']))
        # Find a doctor (first available)
        doctor = User.objects.filter(role='doctor').first()
        if not doctor:
            doctor = user  # Fallback to current user

        dt = datetime.fromisoformat(data['scheduled_at'])
        aware_dt = timezone.make_aware(dt) if timezone.is_naive(dt) else dt

        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            scheduled_at=aware_dt,
            duration=int(data['duration']),
            reason=data['reason'],
            status='planned',
        )
        return {
            'response': (
                f"✅ **Rendez-vous créé avec succès !**\n\n"
                f"• **Patient** : {patient.full_name}\n"
                f"• **Médecin** : Dr. {doctor.last_name or doctor.username}\n"
                f"• **Date** : {appointment.scheduled_at.strftime('%d/%m/%Y à %Hh%M')}\n"
                f"• **Durée** : {appointment.duration} minutes\n"
                f"• **Motif** : {appointment.reason}\n"
                f"• **Statut** : 🟡 Planifié\n\n"
                f"📅 Le rendez-vous est visible dans la liste des rendez-vous !"
            ),
            'actions': ['📅 Planifier un autre RDV', '👤 Ajouter un patient'],
        }, None
    except Exception as e:
        return {'response': f"❌ Erreur lors de la création : {str(e)}"}, None


def detect_creation_intent(message):
    """Détecte si l'utilisateur veut créer un patient ou un RDV."""
    create_kw = ['ajouter', 'creer', 'créer', 'nouveau', 'nouvelle', 'enregistrer', 'inscrire',
                 'ajoute', 'cree', 'créé', 'inscrit', 'saisir']
    patient_kw = ['patient', 'malade', 'personne', 'dossier patient']
    rdv_kw = ['rdv', 'rendez-vous', 'rendez vous', 'appointment', 'rendezvous']

    if match_any(message, create_kw) or match_any(message, ['planifier']):
        if match_any(message, patient_kw):
            return 'create_patient'
        if match_any(message, rdv_kw) or match_any(message, ['planifier']):
            return 'create_appointment'
    return None


def extract_patient_name(message):
    """Extrait rudimentairement un nom de patient d'une phrase."""
    import re
    # Cherche "de [Nom]" ou "nommé [Nom]" ou "patient [Nom]" ou "rendez vous de [Nom]"
    match = re.search(r'(?:de|sur|nommé|patient|dossier(?: de)?)\s+([A-ZÀ-Ÿa-zà-ÿ]+(?:\s+[A-ZÀ-Ÿa-zà-ÿ]+)?)', message, re.IGNORECASE)
    if match:
        name = match.group(1).strip()
        # Filtre les faux positifs évidents
        if name.lower() not in ['quel', 'qui', 'moi', 'mon', 'ce', 'le', 'la', 'les', 'qu\'elle']:
            return name
        
    # Alternative: Prend les mots avec majuscule
    words = message.split()
    caps = [w.strip(',.!?:') for w in words[1:] if w.strip(',.!?:').istitle()]
    if caps:
        return ' '.join(caps)
    return None


# ─────────────────────────────────────────────────────────────
# Main view — AI Driven (NLU)
# ─────────────────────────────────────────────────────────────

# Mapping des intentions du modèle IA vers les handlers Django
INTENT_HANDLERS = {
    'greetings': handle_greetings,
    'thanks': handle_thanks,
    'goodbye': handle_goodbye,
    'identity': handle_identity,
    'patient_search': handle_patient_search,
    'patient_list': handle_patient_list,
    'appointments_view': handle_appointments_upcoming,
    'consultation_info': handle_consultation_info,
    'prescription_info': handle_prescription_info,
    'stats': handle_stats,
    'ia_symptoms': handle_symptoms_ia,
    'help': handle_help,
}

# Handler chain pour le fallback
HANDLERS = [
    handle_greetings,
    handle_thanks,
    handle_goodbye,
    handle_identity,
    handle_user_info,
    handle_patient_search,
    handle_patient_list,
    handle_appointments_upcoming,
    handle_consultation_info,
    handle_prescription_info,
    handle_how_to_patient,
    handle_how_to_appointment,
    handle_how_to_consultation,
    handle_how_to_prescription,
    handle_symptoms_ia,
    handle_stats,
    handle_navigation,
    handle_help,
]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_view(request):
    message = request.data.get('message', '').strip()
    context = request.data.get('context', None)

    if not message:
        return Response({'response': "Veuillez poser une question. 😊"})

    user = request.user

    # 1. ── Flow multi-tour en cours ? ──
    if context and isinstance(context, dict) and context.get('flow'):
        result, _ = process_creation_flow(user, message, context)
        return Response(result)

    # 2. ── Appel au cerveau IA (Brain Service) pour raisonner ──
    from apps.patients.models import Patient
    from apps.appointments.models import Appointment
    
    # Préparation du contexte pour rendre l'IA plus "intelligente"
    try:
        patient_count = Patient.objects.filter(is_archived=False).count()
        today_appts = Appointment.objects.filter(scheduled_at__date=timezone.now().date()).count()
        clinic_context = f"Le cabinet a actuellement {patient_count} patients actifs. Il y a {today_appts} rendez-vous prévus pour aujourd'hui."
        
        r = requests.post(f"{settings.IA_SERVICE_URL}/brain", json={
            'message': message,
            'context': clinic_context
        }, timeout=8)
        brain_data = r.json()
        intent = brain_data.get('intent')
        ai_response = brain_data.get('response') # La réponse fluide type ChatGPT
    except Exception as e:
        print(f"[Chatbot] Brain Service unreachable: {e}")
        intent = detect_creation_intent(message) # Fallback detection logic
        ai_response = None

    # Extraction du nom du patient depuis le message (si renseigné)
    extracted_name = extract_patient_name(message)

    # 3. ── Gestion des flows de création (Spécial) ──
    if intent == 'create_patient' and not context:
        first_step = PATIENT_STEPS[0]
        intro = ai_response if ai_response else "🆕 **Intelligence Artificielle : Création de Patient**\n\nCommençons l'enregistrement."
        return Response({
            'response': f"{intro}\n\n{first_step['question']}",
            'context': {
                'flow': 'create_patient', 'step_index': 0, 'step': 1, 'total_steps': len(PATIENT_STEPS), 'data': {},
            },
        })
    elif intent == 'create_appointment' and not context:
        first_step = APPOINTMENT_STEPS[0]
        intro = ai_response if ai_response else "🆕 **Intelligence Artificielle : Planification RDV**\n\nPlanifions cela ensemble."
        return Response({
            'response': f"{intro}\n\n{first_step['question']}",
            'context': {
                'flow': 'create_appointment', 'step_index': 0, 'step': 1, 'total_steps': len(APPOINTMENT_STEPS), 'data': {},
            },
        })

    # 3.5 --- Nouveau: Cas de diagnostic auto-extrait par l'IA ---
    if intent == 'ia_symptoms' and brain_data.get('symptoms'):
        # On injecte les symptomes pour que le handler ne les cherche pas
        result = handle_symptoms_ia(user, message, prefilled_symptoms=brain_data.get('symptoms'))
        return Response({'response': result})

    # 4. ── Exécution du handler avec réponse augmentée par l'IA ──
    
    # Interception spéciale : demande d'analyse de rendez-vous
    normalized_msg = normalize(message)
    if 'examine' in normalized_msg and 'motif' in normalized_msg and extracted_name:
        result = handle_analyze_appointment(user, extracted_name, ai_response)
        if result:
            return Response({'response': result})

    handler = INTENT_HANDLERS.get(intent)
    if handler:
        # Recherche de patient avec nom extrait dynamiquement
        if intent == 'patient_search' and extracted_name:
            result = handler(user, f"infos sur {extracted_name}")
        else:
            result = handler(user, message)
            
        if result:
            # Si l'IA a généré une intro fluide, on peut l'ajouter
            final_response = f"{ai_response}\n\n{result}" if ai_response and len(result) > 50 else result
            return Response({'response': final_response})

    # 5. ── Fallback : Discussion pure (Si pas d'action technique nécessaire) ──
    if ai_response:
        return Response({'response': ai_response})
    for handler in HANDLERS:
        try:
            result = handler(user, message)
            if result:
                return Response({'response': result})
        except Exception:
            continue

    # 6. ── Réponse par défaut ──
    name = user.first_name or user.username
    return Response({
        'response': (
            f"Désolé **{name}**, mon cerveau NLU n'est pas sûr de comprendre cette demande. 🤖\n\n"
            f"Je peux vous aider pour :\n"
            f"• Rechercher un **patient** ou voir la **liste**\n"
            f"• Créer un **nouveau patient** ou un **RDV**\n"
            f"• Consulter vos **rendez-vous** ou **statistiques**\n"
            f"• Analyser des **symptômes** médicaux\n\n"
            f"Posez-moi votre question différemment ! 😊"
        )
    })


