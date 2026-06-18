import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GROQ_KEY = os.getenv('GROQ_API_KEY', '')

# Initialisation Groq (Llama 3)
if GROQ_KEY:
    try:
        groq_client = Groq(api_key=GROQ_KEY)
    except Exception:
        groq_client = None
else:
    groq_client = None

SYSTEM_PROMPT = """
Tu es l'Assistant IA exclusif de "CuraMedical", un logiciel de gestion pour les professionnels de santé.
L'utilisateur à qui tu t'adresses est un MÉDECIN, une SECRÉTAIRE MÉDICALE ou un ADMINISTRATEUR DE CABINET. Ce n'est JAMAIS le patient.

Règles impératives :
- Réponds en français clair, concis et professionnel.
- Ne t'adresse jamais à l'utilisateur comme s'il était malade ou patient. S'il parle de symptômes (ex: "Il a de la fièvre"), c'est le médecin qui te décrit le cas de son patient pour obtenir Ton analyse ou avis. Tu dois analyser ces symptômes d'un point de vue médical/diagnostique pour assister le professionnel.
- N'invente jamais de données de patients ou de noms.
- Oriente toujours tes suggestions vers l'utilisation du logiciel (ex: "Souhaitez-vous que j'ouvre le dossier du patient ?" ou "Voulez-vous que je crée une consultation pour analyser ce cas ?").
- Tu es un conseiller clinique et logiciel.
"""

PATIENT_SYSTEM_PROMPT = """
Tu es l'assistant médical de la Clinique CuraMedical. Tu parles directement à un PATIENT via WhatsApp.

Règles impératives :
- Réponds en français, avec empathie, clarté et concision (2-4 phrases max).
- Si le patient décrit des symptômes, aide-le à les préciser et oriente-le vers un médecin.
- N'établis JAMAIS de diagnostic médical définitif. Propose des hypothèses générales uniquement.
- En cas de symptômes graves (douleur thoracique, difficulté à respirer, perte de conscience) : appelle le 15 (SAMU) immédiatement.
- Reste rassurant, bienveillant et professionnel.
- Tu peux rappeler que la clinique est disponible pour prendre rendez-vous.
"""


def local_reasoning(message, intent, extracted_name=None, audience='staff'):
    # ── Réponses patient (WhatsApp) ───────────────────────────────────────────
    if audience == 'patient':
        if intent == 'greetings':
            return (
                "Bonjour ! Je suis l'assistant médical de CuraMedical.\n"
                "Décrivez vos symptômes (ex: fièvre, toux, douleur...) et je vous aiderai à les analyser.\n"
                "Pour un rendez-vous ou une urgence, contactez directement la clinique."
            )
        if intent == 'thanks':
            return "De rien ! N'hésitez pas si vous avez d'autres symptômes. Prenez soin de vous."
        if intent in ('ia_symptoms', 'discussion'):
            return "Je vous écoute. Pouvez-vous décrire vos symptômes en détail ?"
        return (
            "Je n'ai pas bien compris votre demande.\n"
            "Essayez de décrire vos symptômes, par exemple : \"j'ai de la fièvre et mal à la gorge\"."
        )

    # ── Réponses staff (interface interne) ────────────────────────────────────
    if intent == 'patient_search':
        if extracted_name:
            return f"Je recherche le dossier de {extracted_name} pour vous afficher les informations les plus utiles."
        return "Precisez le nom du patient et je lancerai la recherche dans le registre."

    if intent == 'create_patient':
        return "Parfait. Nous allons creer un nouveau dossier patient de facon guidee."

    if intent == 'create_appointment':
        return "Tres bien. Nous pouvons planifier un rendez-vous en partant du patient puis du creneau."

    if intent == 'appointments_view':
        return "Je consulte le planning enregistre pour vous presenter les rendez-vous correspondants."

    if intent == 'stats':
        return "Je prepare un apercu synthetique de l activite du cabinet."

    if intent == 'thanks':
        return "Avec plaisir. Je reste disponible pour la suite."

    if intent == 'greetings':
        return "Bonjour. CuraMedical est pret, dites-moi ce que vous souhaitez consulter ou creer."

    if intent == 'discussion':
        return "Je suis a votre ecoute. Dites-moi votre besoin clinique ou organisationnel."

    return f"Je prends en compte votre demande: {message}"


def generate_smart_response(message, intent, extracted_name=None, clinic_context=None, audience='staff'):
    system = PATIENT_SYSTEM_PROMPT if audience == 'patient' else SYSTEM_PROMPT
    prompt = (
        f"Contexte : {clinic_context}\n"
        f"Message : {message}\n"
        f"Intention : {intent}\n"
        + (f"Nom extrait : {extracted_name}\n" if extracted_name else "")
        + "Génère une réponse courte et adaptée."
    )

    if groq_client:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                max_tokens=300
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Erreur Groq (Llama 3): {e}", flush=True)

    return local_reasoning(message, intent, extracted_name, audience=audience)
