import os

import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
# Charger aussi depuis la racine au cas ou
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GEMINI_KEY = os.getenv('GEMINI_API_KEY', '')
GROQ_KEY = os.getenv('GROQ_API_KEY', '')

# Initialisation Gemini
if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        gemini_model = None
else:
    gemini_model = None

# Initialisation Groq (Llama 3)
if GROQ_KEY:
    try:
        groq_client = Groq(api_key=GROQ_KEY)
    except Exception:
        groq_client = None
else:
    groq_client = None

SYSTEM_PROMPT = """
Tu es l'Assistant IA exclusif de "MedPredict", un logiciel de gestion pour les professionnels de santé.
L'utilisateur à qui tu t'adresses est un MÉDECIN, une SECRÉTAIRE MÉDICALE ou un ADMINISTRATEUR DE CABINET. Ce n'est JAMAIS le patient.

Règles impératives :
- Réponds en français clair, concis et professionnel.
- Ne t'adresse jamais à l'utilisateur comme s'il était malade ou patient. S'il parle de symptômes (ex: "Il a de la fièvre"), c'est le médecin qui te décrit le cas de son patient pour obtenir Ton analyse ou avis. Tu dois analyser ces symptômes d'un point de vue médical/diagnostique pour assister le professionnel.
- N'invente jamais de données de patients ou de noms.
- Oriente toujours tes suggestions vers l'utilisation du logiciel (ex: "Souhaitez-vous que j'ouvre le dossier du patient ?" ou "Voulez-vous que je crée une consultation pour analyser ce cas ?").
- Tu es un conseiller clinique et logiciel.
"""


def local_reasoning(message, intent, extracted_name=None):
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
        return "Bonjour. MedPredict est pret, dites-moi ce que vous souhaitez consulter ou creer."

    if intent == 'discussion':
        return "Je suis a votre ecoute. Dites-moi votre besoin clinique ou organisationnel."

    return f"Je prends en compte votre demande: {message}"


def generate_smart_response(message, intent, extracted_name=None, clinic_context=None):
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Contexte applicatif: {clinic_context}\n"
        f"Message utilisateur: {message}\n"
        f"Intention détectée: {intent}\n"
        f"Nom extrait: {extracted_name}\n\n"
        "Génère une réponse courte, professionnelle et orientée action."
    )

    # 1. Tentative avec Meta Llama 3 via Groq (Priorité car demandé par l'utilisateur)
    if groq_client:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=500
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Erreur Groq (Llama 3): {e}")

    # 2. Fallback vers Gemini 1.5 Flash
    if gemini_model:
        try:
            response = gemini_model.generate_content(prompt)
            if getattr(response, 'text', None):
                return response.text
        except Exception as e:
            print(f"Erreur Gemini: {e}")

    return local_reasoning(message, intent, extracted_name)
