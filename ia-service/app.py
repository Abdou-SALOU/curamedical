import os
import re
import subprocess
import sys
import json

import joblib
import numpy as np
from flask import Flask, jsonify, request

from intent_classifier import INTENT_MODEL_PATH, predict_intent, train_intents
from reasoning_engine import generate_smart_response, gemini_model, groq_client

app = Flask(__name__)

MODEL_PATH = 'model/classifier.pkl'
ENCODER_PATH = 'model/label_encoder.pkl'
FEATURES_PATH = 'model/features_list.pkl'

model = None
encoder = None
features = []
intent_model = None

def train_model():
    print('Model diagnostic absent, lancement de train.py...')
    subprocess.run([sys.executable, 'train.py'], check=True)
    print('Entrainement termine.')

def load_model():
    global model, encoder, features, intent_model
    if not os.path.exists(MODEL_PATH):
        if os.getenv('FLASK_ENV') == 'production':
            print(f"❌ Erreur critique : Modèle absent à {MODEL_PATH}. L'entraînement automatique est désactivé en production.")
            return
        train_model()

    try:
        model = joblib.load(MODEL_PATH)
        encoder = joblib.load(ENCODER_PATH)
        features = joblib.load(FEATURES_PATH)
        intent_model = joblib.load(INTENT_MODEL_PATH) if os.path.exists(INTENT_MODEL_PATH) else train_intents()

        print(f'✅ Modele diagnostic charge: {len(encoder.classes_)} maladies')
        print(f'✅ Liste des features chargee: {len(features)} symptomes')
    except Exception as e:
        print(f"❌ Erreur lors du chargement des modeles: {e}")

def get_symptoms_via_llm(text):
    """Utilise Groq (ou Gemini) pour extraire les symptômes médicaux en anglais correspondant à notre features_list."""
    
    prompt = f"""
    En tant qu'assistant médical, extrais les symptômes du texte suivant : "{text}"
    Fais-les correspondre STRICTEMENT et UNIQUEMENT aux éléments de la liste suivante (en anglais) :
    {json.dumps(features)}
    
    Réponds uniquement avec un code JSON valide. Ça doit être un simple tableau contenant les noms exacts trouvés dans la liste, ou un tableau vide []. Il ne doit y avoir AUCUN autre texte retourné.
    Exemple de réponse attendue : ["fever", "cough"]
    """
    
    if groq_client:
        try:
            resp = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=150
            )
            content = resp.choices[0].message.content
            match = re.search(r'\[.*\]', content.replace('\n', ''), re.DOTALL)
            if match:
                extracted = json.loads(match.group(0))
                return [s for s in extracted if s in features]
        except Exception as e:
            print(f"Groq Extract Error: {e}")

    if gemini_model:
        try:
            response = gemini_model.generate_content(prompt)
            match = re.search(r'\[.*\]', response.text.replace('\n', ''), re.DOTALL)
            if match:
                extracted = json.loads(match.group(0))
                return [s for s in extracted if s in features]
        except Exception as e:
            print(f"Gemini Extract Error: {e}")
            
    return []

def encode_patient_profile(payload):
    input_symptoms = payload.get('symptoms', [])
    if isinstance(input_symptoms, str):
        input_symptoms = [s.strip() for s in input_symptoms.split(',')]
    
    vector = np.zeros(len(features))
    for i, f in enumerate(features):
        if f in input_symptoms:
            vector[i] = 1
            
    return vector.reshape(1, -1), input_symptoms

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Modele non charge'}), 503

    payload = request.get_json() or {}
    symptoms = payload.get('symptoms', [])
    
    # Si les symptomes sont vides dans le payload mais qu'il y a un message texte
    message = payload.get('message', '')
    if not symptoms and message:
        symptoms = get_symptoms_via_llm(message)

    # Mappage complet Français -> Anglais pour tous les symptômes du formulaire
    fr_to_en = {
        'fièvre': 'fever',
        'toux': 'cough',
        'fatigue': 'fatigue',
        'difficulté respiratoire': 'breathlessness',
        'essoufflement': 'breathlessness',
        'dyspnée': 'breathlessness',
        'maux de tête': 'headache',
        'céphalées': 'headache',
        'vomissements': 'vomiting',
        'nausées': 'nausea',
        'diarrhée': 'diarrhoea',
        'douleur abdominale': 'abdominal_pain',
        'douleur au ventre': 'abdominal_pain',
        'douleur thoracique': 'chest_pain',
        'douleur poitrine': 'chest_pain',
        'douleur dorsale': 'back_pain',
        'douleurs lombaires': 'back_pain',
        'douleurs articulaires': 'joint_pain',
        'éruption cutanée': 'skin_rash',
        'boutons': 'skin_rash',
        'démangeaisons': 'skin_rash',
        'perte de poids': 'weight_loss',
        'amaigrissement': 'weight_loss',
        'perte d\'appétit': 'loss_of_appetite',
        'anorexie': 'loss_of_appetite',
        'transpiration': 'sweating',
        'sueurs': 'sweating',
        'frissons': 'chills',
        'vertiges': 'dizziness',
        'ganglions gonflés': 'swollen_lymph_nodes',
        'adénopathie': 'swollen_lymph_nodes',
        'jaunisse': 'yellowish_skin',
    }

    # Dictionnaire de traduction des maladies Anglais -> Français
    en_to_fr_disease = {
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
        '(vertigo) Paroymsal  Positional Vertigo': 'Vertige positionnel paroxystique bénin',
        'Acne': 'Acné',
        'Urinary tract infection': 'Infection urinaire',
        'Psoriasis': 'Psoriasis',
        'Impetigo': 'Impétigo',
        'viral warts': 'Verrues virales',
    }

    input_symptoms_translated = []
    for s in symptoms:
        s_low = s.lower().strip()
        input_symptoms_translated.append(fr_to_en.get(s_low, s_low))

    vector, final_symptoms = encode_patient_profile({'symptoms': input_symptoms_translated})
    probabilities = model.predict_proba(vector)[0]
    top_indices = np.argsort(probabilities)[-3:][::-1]

    suggestions = []
    for index in top_indices:
        confidence = float(probabilities[index]) * 100
        disease_en = encoder.classes_[index]
        disease_fr = en_to_fr_disease.get(disease_en, disease_en)
        
        suggestions.append({
            'disease': disease_fr,
            'confidence': round(confidence, 1),
            'risk_level': 'eleve' if confidence > 70 else ('modere' if confidence > 30 else 'faible'),
            'explanation': f"Hypothèse suggérée par l'IA en fonction des symptômes : {', '.join(final_symptoms)}."
        })

    # Si rien n'est assez sur, on informe que les donnees sont trop vagues
    if not suggestions and final_symptoms:
        suggestions.append({
            'disease': 'Indéterminé (Manque de précision)',
            'confidence': 0,
            'risk_level': '—',
            'explanation': f"Les symptômes ({', '.join(final_symptoms)}) sont trop généraux pour une suggestion IA. Ajoutez plus de détails cliniques."
        })

    return jsonify({'suggestions': suggestions})

@app.route('/brain', methods=['POST'])
def brain_endpoint():
    if intent_model is None:
        return jsonify({'error': 'IA non initialisee'}), 503

    data = request.get_json() or {}
    message = data.get('message', '').strip()
    clinic_context = data.get('context', '') # Récupération du contexte clinique du backend
    
    if not message:
        return jsonify({'intent': 'none', 'response': 'Bonjour !'})

    intent = predict_intent(message, intent_model)
    
    # Si l'intention semble etre des symptomes, on preempt l'extraction
    extracted_symptoms = []
    if any(kw in message.lower() for kw in ['j\'ai', 'souffre', 'symptome', 'mal au', 'douleur', 'fievre', 'toux']):
        extracted_symptoms = get_symptoms_via_llm(message)
        if extracted_symptoms:
            return jsonify({
                'intent': 'ia_symptoms',
                'response': f"J'ai identifié les symptômes suivants : {', '.join(extracted_symptoms)}. Lancement de l'analyse...",
                'symptoms': extracted_symptoms
            })

    smart_response = generate_smart_response(message, intent, clinic_context=clinic_context)
    return jsonify({
        'intent': intent,
        'response': smart_response,
    })

@app.route('/symptoms', methods=['GET'])
def get_symptoms():
    return jsonify({'symptoms': features})

if __name__ == '__main__':
    load_model()
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
