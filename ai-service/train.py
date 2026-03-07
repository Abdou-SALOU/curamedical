"""
Script d'entraînement du modèle de classification des symptômes.
Dataset : symptom_disease dataset (Kaggle public)
Lancer avec : python train.py
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

os.makedirs('model', exist_ok=True)

# Dataset embarqué (version simplifiée pour démarrer)
# En production : remplacer par le vrai dataset Kaggle
DATA = {
    'symptoms': [
        ['fever', 'cough', 'fatigue'],
        ['fever', 'cough', 'shortness_of_breath'],
        ['headache', 'fever', 'stiff_neck'],
        ['stomach_pain', 'nausea', 'vomiting'],
        ['chest_pain', 'shortness_of_breath', 'fatigue'],
        ['fever', 'rash', 'joint_pain'],
        ['cough', 'night_sweats', 'weight_loss'],
        ['frequent_urination', 'fatigue', 'increased_thirst'],
        ['headache', 'nausea', 'sensitivity_to_light'],
        ['fever', 'cough', 'runny_nose'],
        ['chest_pain', 'fever', 'cough'],
        ['abdominal_pain', 'fever', 'jaundice'],
    ],
    'disease': [
        'Grippe', 'Pneumonie', 'Méningite',
        'Gastro-entérite', 'Insuffisance cardiaque', 'Dengue',
        'Tuberculose', 'Diabète', 'Migraine',
        'Rhume', 'Pleurésie', 'Hépatite',
    ]
}

# Construction du dataset
all_symptoms = list(set(
    s for symptoms in DATA['symptoms'] for s in symptoms
))
all_symptoms.sort()

X = []
for symptoms in DATA['symptoms']:
    vector = [1 if s in symptoms else 0 for s in all_symptoms]
    X.append(vector)

y = DATA['disease']
X = np.array(X)

# Entraînement
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Évaluation
y_pred = clf.predict(X_test)
print(f"✅ Précision du modèle : {accuracy_score(y_test, y_pred) * 100:.1f}%")

# Sauvegarde
joblib.dump(clf, 'model/classifier.pkl')
joblib.dump(all_symptoms, 'model/symptoms_list.pkl')
joblib.dump(list(clf.classes_), 'model/diseases_list.pkl')

print(f"✅ Modèle sauvegardé — {len(all_symptoms)} symptômes")
print(f"✅ Maladies : {list(clf.classes_)}")