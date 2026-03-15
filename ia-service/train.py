import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import joblib
import os

os.makedirs('model', exist_ok=True)

# ── 1. Chargement du dataset ──────────────────────────────────────────────────
df = pd.read_csv('data/Disease_symptom_and_patient_profile_dataset.csv')
print(f"✅ Dataset chargé : {len(df)} lignes, {df['Disease'].nunique()} maladies")

# ── 2. Nettoyage ──────────────────────────────────────────────────────────────
df = df.dropna()
df.columns = df.columns.str.strip()

# ── 3. Encodage des features ──────────────────────────────────────────────────

# Binaire Yes/No
binary_cols = ['Fever', 'Cough', 'Fatigue', 'Difficulty Breathing']
for col in binary_cols:
    df[col] = df[col].map({'Yes': 1, 'No': 0})

# Genre
df['Gender'] = df['Gender'].map({'Male': 1, 'Female': 0})

# Pression artérielle
df['Blood Pressure'] = df['Blood Pressure'].map({
    'Low': 0, 'Normal': 1, 'High': 2
})

# Cholestérol
df['Cholesterol Level'] = df['Cholesterol Level'].map({
    'Low': 0, 'Normal': 1, 'High': 2
})

# Tranche d'âge
def age_group(age):
    if age < 18:   return 0  # enfant
    if age < 35:   return 1  # jeune adulte
    if age < 50:   return 2  # adulte
    if age < 65:   return 3  # senior
    return 4                 # âgé

df['Age Group'] = df['Age'].apply(age_group)

# ── 4. Features et cible ──────────────────────────────────────────────────────
FEATURES = [
    'Fever', 'Cough', 'Fatigue', 'Difficulty Breathing',
    'Gender', 'Blood Pressure', 'Cholesterol Level', 'Age Group'
]

X = df[FEATURES]
y = df['Disease']

# ── 5. Encodage des labels ────────────────────────────────────────────────────
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# ── 6. Split train/test ───────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# ── 7. Entraînement ───────────────────────────────────────────────────────────
clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=2,
    random_state=42,
    class_weight='balanced'  # gère le déséquilibre des classes
)
clf.fit(X_train, y_train)

# ── 8. Évaluation ─────────────────────────────────────────────────────────────
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Précision : {accuracy * 100:.1f}%")
print(f"\n📊 Rapport de classification :")
print(classification_report(y_test, y_pred, zero_division=0))

# ── 9. Sauvegarde ─────────────────────────────────────────────────────────────
joblib.dump(clf, 'model/classifier.pkl')
joblib.dump(le,  'model/label_encoder.pkl')
joblib.dump(FEATURES, 'model/features_list.pkl')

print(f"\n✅ Modèle sauvegardé !")
print(f"   Features : {FEATURES}")
print(f"   Maladies : {len(le.classes_)}")