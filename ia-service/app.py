from flask import Flask, request, jsonify
import joblib
import numpy as np
import os

app = Flask(__name__)

# Chargement du modèle (sera créé par train.py)
MODEL_PATH = 'model/classifier.pkl'
SYMPTOMS_PATH = 'model/symptoms_list.pkl'
DISEASES_PATH = 'model/diseases_list.pkl'

model = None
symptoms_list = []
diseases_list = []

def load_model():
    global model, symptoms_list, diseases_list
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        symptoms_list = joblib.load(SYMPTOMS_PATH)
        diseases_list = joblib.load(DISEASES_PATH)
        print(f"✅ Modèle chargé — {len(symptoms_list)} symptômes, {len(diseases_list)} maladies")
    else:
        print("⚠️  Modèle non trouvé — lancez train.py d'abord")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None
    })

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Modèle non chargé'}), 503

    data = request.get_json()
    symptoms_input = data.get('symptoms', [])

    if not symptoms_input:
        return jsonify({'error': 'Aucun symptôme fourni'}), 400

    # Encodage binaire des symptômes
    input_vector = np.zeros(len(symptoms_list))
    for symptom in symptoms_input:
        symptom_clean = symptom.lower().strip()
        if symptom_clean in symptoms_list:
            idx = symptoms_list.index(symptom_clean)
            input_vector[idx] = 1

    # Prédiction avec probabilités
    probabilities = model.predict_proba([input_vector])[0]
    top_3_indices = np.argsort(probabilities)[-3:][::-1]

    suggestions = []
    for idx in top_3_indices:
        if probabilities[idx] > 0:
            suggestions.append({
                'disease': diseases_list[idx],
                'confidence': round(float(probabilities[idx]) * 100, 1)
            })

    return jsonify({
        'suggestions': suggestions,
        'disclaimer': 'Outil d\'aide — ne remplace pas le diagnostic médical'
    })

@app.route('/symptoms', methods=['GET'])
def get_symptoms():
    """Retourne la liste de tous les symptômes disponibles"""
    return jsonify({'symptoms': symptoms_list})

if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=5000, debug=True)