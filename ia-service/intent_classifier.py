import os
import re
import unicodedata

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from intents_data import INTENTS

INTENT_MODEL_PATH = 'model/intent_classifier.pkl'


def normalize_fr(text):
    text = text.lower().strip()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[?!.]+$", '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def train_intents():
    print('Entrainement du classifieur d intentions...')

    examples = []
    labels = []

    for intent, samples in INTENTS.items():
        for sample in samples:
            examples.append(normalize_fr(sample))
            labels.append(intent)

    pipeline = Pipeline(
        [
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ('clf', LinearSVC(C=1.0, random_state=42)),
        ]
    )
    pipeline.fit(examples, labels)

    os.makedirs('model', exist_ok=True)
    joblib.dump(pipeline, INTENT_MODEL_PATH)
    print(f'Classifieur entraine avec succes ({len(examples)} exemples, {len(INTENTS)} intentions)')
    return pipeline


def predict_intent(text, model=None):
    classifier = model
    if classifier is None:
        classifier = train_intents() if not os.path.exists(INTENT_MODEL_PATH) else joblib.load(INTENT_MODEL_PATH)
    return classifier.predict([normalize_fr(text)])[0]


if __name__ == '__main__':
    train_intents()
