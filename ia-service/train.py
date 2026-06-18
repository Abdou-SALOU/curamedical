print("Démarrage du script d'entraînement...")
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os

print("Modules importés.")
# Create model directory
os.makedirs('model', exist_ok=True)

DATASET_PATH = 'Fast_Dataset.csv'

# 1. Load dataset
if not os.path.exists(DATASET_PATH):
    print(f"Error: Dataset {DATASET_PATH} not found.")
    exit(1)

try:
    df = pd.read_csv(DATASET_PATH)
    print(f"Loaded dataset: {len(df)} rows, {df['diseases'].nunique()} diseases")
except Exception as e:
    print(f"Error reading CSV: {e}")
    exit(1)

# 2. Cleanup
df = df.dropna()
target_col = 'diseases'
FEATURES = [col for col in df.columns if col != target_col]

X = df[FEATURES]
y = df[target_col]

# 3. Encoding
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# 4. Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.1, random_state=42
)

# 5. Stronger Training (Random Forest)
print(f"Training RandomForestClassifier on {len(FEATURES)} symptoms...")
clf = RandomForestClassifier(n_estimators=30, random_state=42)
clf.fit(X_train, y_train)

# 6. Evaluation
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.1f}%")

# 7. Save
print("Sauvegarde des modèles...")
joblib.dump(clf, 'model/classifier.pkl')
joblib.dump(le,  'model/label_encoder.pkl')
joblib.dump(FEATURES, 'model/features_list.pkl')

print(f"\nModel updated and saved successfully!")
print(f"   Symptoms count: {len(FEATURES)}")
print(f"   Diseases count: {len(le.classes_)}")