from flask import Flask, request, jsonify
import joblib
import numpy as np
import os

app = Flask(__name__)

MODEL_PATH    = 'model/classifier.pkl'
ENCODER_PATH  = 'model/label_encoder.pkl'
FEATURES_PATH = 'model/features_list.pkl'

model    = None
encoder  = None
features = []

def train_model():
    """Entraîne le modèle si absent"""
    print("🔄 Modèle absent — entraînement en cours...")
    import subprocess
    subprocess.run(['python', 'train.py'], check=True)
    print("✅ Entraînement terminé !")

def load_model():
    global model, encoder, features
    if not os.path.exists(MODEL_PATH):
        train_model()
    model    = joblib.load(MODEL_PATH)
    encoder  = joblib.load(ENCODER_PATH)
    features = joblib.load(FEATURES_PATH)
    print(f"✅ Modèle chargé — {len(encoder.classes_)} maladies")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'model_loaded': model is not None,
        'diseases_count': len(encoder.classes_) if encoder else 0
    })

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Modèle non chargé'}), 503

    data        = request.get_json()
    symptoms    = data.get('symptoms', [])
    age         = data.get('age', 30)
    gender      = data.get('gender', 'M')
    bp          = data.get('blood_pressure', 'Normal')
    cholesterol = data.get('cholesterol', 'Normal')

    fever     = 1 if 'fever'                in symptoms else 0
    cough     = 1 if 'cough'                in symptoms else 0
    fatigue   = 1 if 'fatigue'              in symptoms else 0
    breathing = 1 if 'difficulty_breathing' in symptoms else 0

    gender_enc = 1 if gender == 'M' else 0
    bp_enc     = {'Low': 0, 'Normal': 1, 'High': 2}.get(bp, 1)
    chol_enc   = {'Low': 0, 'Normal': 1, 'High': 2}.get(cholesterol, 1)

    def age_group(a):
        if a < 18: return 0
        if a < 35: return 1
        if a < 50: return 2
        if a < 65: return 3
        return 4

    input_vector = np.array([[
        fever, cough, fatigue, breathing,
        gender_enc, bp_enc, chol_enc, age_group(age)
    ]])

    probabilities = model.predict_proba(input_vector)[0]
    top_3_indices = np.argsort(probabilities)[-3:][::-1]

    suggestions = []
    for idx in top_3_indices:
        if probabilities[idx] > 0:
            suggestions.append({
                'disease':    encoder.classes_[idx],
                'confidence': round(float(probabilities[idx]) * 100, 1)
            })

    return jsonify({
        'suggestions': suggestions,
        'disclaimer': "Outil d'aide — ne remplace pas le diagnostic médical"
    })

@app.route('/symptoms', methods=['GET'])
def get_symptoms():
    return jsonify({
        'symptoms': ['fever', 'cough', 'fatigue', 'difficulty_breathing'],
        'other_params': {
            'gender':         ['M', 'F'],
            'blood_pressure': ['Low', 'Normal', 'High'],
            'cholesterol':    ['Low', 'Normal', 'High'],
        }
    })

if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=5000, debug=True)