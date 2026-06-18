import os
import re
import subprocess
import sys
import json

import joblib
import numpy as np
from flask import Flask, jsonify, request

from intent_classifier import INTENT_MODEL_PATH, predict_intent, train_intents
from reasoning_engine import generate_smart_response, groq_client

app = Flask(__name__)

# ─────────────────────────────────────────────
# Constantes — définies au niveau module (une seule fois, pas à chaque requête)
# ─────────────────────────────────────────────

MODEL_PATH = 'model/classifier.pkl'
ENCODER_PATH = 'model/label_encoder.pkl'
FEATURES_PATH = 'model/features_list.pkl'

# Traduction Français → Anglais pour les symptômes (multi-alias, couvre ~300 termes courants)
FR_TO_EN = {
    # ── Fièvre / Température ──────────────────────────────────────────────────
    'fièvre': 'fever', 'fievre': 'fever', 'temperature': 'fever',
    'hyperthermie': 'fever', 'forte fièvre': 'fever', 'forte fievre': 'fever',
    'fébricule': 'fever', 'febricule': 'fever', 'chaud': 'fever',
    'avoir de la fièvre': 'fever', 'avoir de la fievre': 'fever',

    # ── Toux ─────────────────────────────────────────────────────────────────
    'toux': 'cough', 'tousser': 'cough', 'toux sèche': 'cough',
    'toux seche': 'cough', 'toux grasse': 'coughing up sputum',
    'toux productive': 'coughing up sputum', 'expectoration': 'coughing up sputum',
    'crachat': 'coughing up sputum', 'crachats': 'coughing up sputum',
    'toux avec sang': 'hemoptysis', 'crachats de sang': 'hemoptysis',
    'hémoptysie': 'hemoptysis', 'hemoptysie': 'hemoptysis',

    # ── Fatigue / Épuisement ──────────────────────────────────────────────────
    'fatigue': 'fatigue', 'épuisement': 'fatigue', 'epuisement': 'fatigue',
    'asthénie': 'fatigue', 'asthenie': 'fatigue', 'manque d\'énergie': 'fatigue',
    'manque d\'energie': 'fatigue', 'fatigué': 'fatigue', 'fatigue': 'fatigue',

    # ── Difficultés respiratoires ─────────────────────────────────────────────
    'difficulté respiratoire': 'shortness of breath',
    'difficulte respiratoire': 'shortness of breath',
    'essoufflement': 'shortness of breath', 'dyspnée': 'shortness of breath',
    'dyspnee': 'shortness of breath', 'difficile de respirer': 'shortness of breath',
    'difficulté à respirer': 'shortness of breath',
    'difficulte a respirer': 'shortness of breath',
    'manque d\'air': 'shortness of breath', 'respiration difficile': 'shortness of breath',
    'oppression thoracique': 'chest tightness', 'serrement de poitrine': 'chest tightness',
    'poitrine serrée': 'chest tightness', 'poitrine serree': 'chest tightness',
    'respiration sifflante': 'wheezing', 'sifflement respiratoire': 'wheezing',
    'sibilances': 'wheezing', 'respiration rapide': 'breathing fast',
    'halètement': 'breathing fast', 'haletement': 'breathing fast',
    'apnée': 'apnea', 'apnee': 'apnea',
    'douleur à la respiration': 'hurts to breath', 'douleur en respirant': 'hurts to breath',

    # ── Maux de tête ─────────────────────────────────────────────────────────
    'maux de tête': 'headache', 'maux de tete': 'headache',
    'mal de tête': 'headache', 'mal de tete': 'headache',
    'céphalées': 'headache', 'cephalees': 'headache',
    'migraine': 'headache', 'tête qui fait mal': 'headache',
    'tete qui fait mal': 'headache', 'céphalée frontale': 'frontal headache',
    'cephalee frontale': 'frontal headache', 'douleur frontale': 'frontal headache',

    # ── Nausées / Vomissements ────────────────────────────────────────────────
    'nausées': 'nausea', 'nausees': 'nausea', 'nausée': 'nausea', 'nausee': 'nausea',
    'envie de vomir': 'nausea', 'mal au cœur': 'nausea', 'mal au coeur': 'nausea',
    'vomissements': 'vomiting', 'vomissement': 'vomiting', 'vomir': 'vomiting',
    'vomit': 'vomiting', 'régurgitation': 'regurgitation', 'regurgitation': 'regurgitation',
    'vomissement de sang': 'vomiting blood', 'vomit du sang': 'vomiting blood',

    # ── Diarrhée / Constipation ───────────────────────────────────────────────
    'diarrhée': 'diarrhea', 'diarrhee': 'diarrhea', 'selles liquides': 'diarrhea',
    'selles molles': 'diarrhea', 'intestins': 'diarrhea',
    'constipation': 'constipation', 'difficile d\'aller à la selle': 'constipation',
    'sang dans les selles': 'blood in stool', 'selles noires': 'melena',
    'méléna': 'melena', 'melena': 'melena', 'rectorragie': 'rectal bleeding',
    'saignement rectal': 'rectal bleeding', 'ballonnements': 'stomach bloating',
    'ventre gonflé': 'stomach bloating', 'ventre gonfle': 'stomach bloating',
    'flatulences': 'flatulence', 'gaz': 'flatulence', 'aérophagie': 'flatulence',

    # ── Douleurs abdominales ──────────────────────────────────────────────────
    'douleur abdominale': 'sharp abdominal pain',
    'douleur au ventre': 'sharp abdominal pain',
    'mal au ventre': 'sharp abdominal pain',
    'crampes abdominales': 'sharp abdominal pain',
    'douleur en haut du ventre': 'upper abdominal pain',
    'douleur abdominale haute': 'upper abdominal pain',
    'douleur à l\'estomac': 'upper abdominal pain', 'mal à l\'estomac': 'upper abdominal pain',
    'douleur abdominale basse': 'lower abdominal pain',
    'douleur au bas-ventre': 'lower abdominal pain', 'douleur au bas ventre': 'lower abdominal pain',
    'brûlures d\'estomac': 'heartburn', 'brulures d\'estomac': 'heartburn',
    'reflux': 'heartburn', 'acidité': 'heartburn', 'acidite': 'heartburn',
    'douleur abdominale brûlante': 'burning abdominal pain',

    # ── Douleurs thoraciques ──────────────────────────────────────────────────
    'douleur thoracique': 'sharp chest pain', 'douleur à la poitrine': 'sharp chest pain',
    'douleur poitrine': 'sharp chest pain', 'mal à la poitrine': 'sharp chest pain',
    'mal au thorax': 'sharp chest pain', 'douleur cardiaque': 'sharp chest pain',
    'douleur thoracique brûlante': 'burning chest pain',
    'brûlure thoracique': 'burning chest pain',

    # ── Douleurs dorsales / Lombaires ─────────────────────────────────────────
    'douleur dorsale': 'back pain', 'mal de dos': 'back pain',
    'douleur au dos': 'back pain', 'douleur dans le dos': 'back pain',
    'douleurs lombaires': 'low back pain', 'lombalgie': 'low back pain',
    'lumbago': 'low back pain', 'mal aux reins': 'low back pain',
    'douleur lombaire': 'low back pain', 'raideur du dos': 'back stiffness or tightness',
    'dos raide': 'back stiffness or tightness', 'crampes dans le dos': 'back cramps or spasms',

    # ── Douleurs articulaires / Musculaires ───────────────────────────────────
    'douleurs articulaires': 'joint pain', 'douleur articulaire': 'joint pain',
    'arthralgie': 'joint pain', 'gonflement articulaire': 'joint swelling',
    'articulations gonflées': 'joint swelling', 'raideur articulaire': 'joint stiffness or tightness',
    'douleur musculaire': 'muscle pain', 'myalgie': 'muscle pain',
    'douleurs musculaires': 'muscle pain', 'mal aux muscles': 'muscle pain',
    'crampes musculaires': 'muscle pain', 'contracture musculaire': 'muscle pain',
    'raideur musculaire': 'muscle stiffness or tightness',
    'faiblesse musculaire': 'muscle weakness', 'muscles faibles': 'muscle weakness',

    # ── Membres / Extrémités ──────────────────────────────────────────────────
    'douleur aux jambes': 'leg pain', 'mal aux jambes': 'leg pain',
    'douleur dans les jambes': 'leg pain', 'jambes douloureuses': 'leg pain',
    'gonflement des jambes': 'leg swelling', 'jambes enflées': 'leg swelling',
    'jambe gonflée': 'leg swelling', 'crampes aux jambes': 'leg cramps or spasms',
    'faiblesse des jambes': 'leg weakness', 'jambes faibles': 'leg weakness',
    'douleur au genou': 'knee pain', 'genou douloureux': 'knee pain',
    'genou gonflé': 'knee swelling', 'gonflement du genou': 'knee swelling',
    'douleur à la cheville': 'ankle pain', 'cheville douloureuse': 'ankle pain',
    'cheville gonflée': 'ankle swelling', 'gonflement de la cheville': 'ankle swelling',
    'douleur au pied': 'foot or toe pain', 'mal au pied': 'foot or toe pain',
    'pieds gonflés': 'foot or toe swelling', 'gonflement des pieds': 'foot or toe swelling',
    'douleur à l\'épaule': 'shoulder pain', 'douleur épaule': 'shoulder pain',
    'épaule douloureuse': 'shoulder pain', 'douleur au bras': 'arm pain',
    'mal au bras': 'arm pain', 'bras douloureux': 'arm pain',
    'douleur au coude': 'elbow pain', 'coude douloureux': 'elbow pain',
    'douleur au poignet': 'wrist pain', 'poignet douloureux': 'wrist pain',
    'douleur à la main': 'hand or finger pain', 'douleur aux doigts': 'hand or finger pain',
    'douleur au cou': 'neck pain', 'mal au cou': 'neck pain',
    'torticolis': 'neck stiffness or tightness', 'cou raide': 'neck stiffness or tightness',
    'douleur à la hanche': 'hip pain', 'hanche douloureuse': 'hip pain',
    'douleurs osseuses': 'bones are painful', 'os douloureux': 'bones are painful',

    # ── Peau ─────────────────────────────────────────────────────────────────
    'éruption cutanée': 'skin rash', 'eruption cutanee': 'skin rash',
    'rash cutané': 'skin rash', 'rash': 'skin rash',
    'boutons': 'acne or pimples', 'acné': 'acne or pimples', 'acne': 'acne or pimples',
    'démangeaisons cutanées': 'itching of skin', 'demangeaisons cutanees': 'itching of skin',
    'prurit': 'itching of skin', 'peau qui gratte': 'itching of skin',
    'démangeaisons': 'itching of skin', 'demangeaisons': 'itching of skin',
    'peau sèche': 'skin dryness, peeling, scaliness, or roughness',
    'peau seche': 'skin dryness, peeling, scaliness, or roughness',
    'peau qui pèle': 'skin dryness, peeling, scaliness, or roughness',
    'peau irritée': 'skin irritation', 'irritation cutanée': 'skin irritation',
    'irritation de la peau': 'skin irritation', 'lésion cutanée': 'skin lesion',
    'jaunisse': 'jaundice', 'ictère': 'jaundice', 'icte': 'jaundice',
    'peau jaune': 'jaundice', 'yeux jaunes': 'jaundice',
    'pâleur': 'pallor', 'paleur': 'pallor', 'teint pâle': 'pallor',
    'verrues': 'warts', 'verrue': 'warts',

    # ── Poids / Appétit ───────────────────────────────────────────────────────
    'perte de poids': 'recent weight loss', 'amaigrissement': 'recent weight loss',
    'maigrir': 'recent weight loss', 'perdre du poids': 'recent weight loss',
    'prise de poids': 'weight gain', 'grossir': 'weight gain',
    "perte d'appétit": 'decreased appetite', 'perte d appetit': 'decreased appetite',
    'anorexie': 'decreased appetite', 'pas faim': 'decreased appetite',
    'manque d\'appétit': 'decreased appetite', 'manque d appetit': 'decreased appetite',
    'appétit excessif': 'excessive appetite', 'manger beaucoup': 'excessive appetite',

    # ── Gorge / Nez / ORL ─────────────────────────────────────────────────────
    'mal de gorge': 'sore throat', 'gorge irritée': 'sore throat',
    'gorge douloureuse': 'sore throat', 'gorge qui fait mal': 'sore throat',
    'angine': 'sore throat', 'gorge rouge': 'sore throat',
    'nez bouché': 'nasal congestion', 'nez bouche': 'nasal congestion',
    'congestion nasale': 'nasal congestion', 'nez congestionné': 'nasal congestion',
    'nez qui coule': 'coryza', 'rhinite': 'coryza', 'écoulement nasal': 'coryza',
    'écoulement nasal': 'coryza', 'rhinorrhée': 'coryza',
    'éternuements': 'sneezing', 'eternuements': 'sneezing', 'éternuer': 'sneezing',
    'sinusite': 'sinus congestion', 'douleurs sinusales': 'painful sinuses',
    'congestion des sinus': 'sinus congestion',
    'voix rauque': 'hoarse voice', 'enrouement': 'hoarse voice', 'voix cassée': 'hoarse voice',
    'difficulté à avaler': 'difficulty in swallowing', 'dysphagie': 'difficulty in swallowing',
    'mal à avaler': 'difficulty in swallowing', 'avaler difficile': 'difficulty in swallowing',
    'amygdales gonflées': 'swollen or red tonsils', 'angine de poitrine': 'swollen or red tonsils',
    'saignement de nez': 'nosebleed', 'épistaxis': 'nosebleed', 'nez qui saigne': 'nosebleed',

    # ── Oreilles ──────────────────────────────────────────────────────────────
    'douleur à l\'oreille': 'ear pain', 'mal à l\'oreille': 'ear pain',
    'otalgie': 'ear pain', 'oreille douloureuse': 'ear pain',
    'bourdonnements': 'ringing in ear', 'acouphènes': 'ringing in ear',
    'acouphene': 'ringing in ear', 'tinnitus': 'ringing in ear',
    'oreille bouchée': 'plugged feeling in ear', 'oreille bouchee': 'plugged feeling in ear',
    'perte d\'audition': 'diminished hearing', 'surdité': 'diminished hearing',
    'entendre mal': 'diminished hearing',

    # ── Yeux ──────────────────────────────────────────────────────────────────
    'douleur à l\'œil': 'pain in eye', 'douleur oculaire': 'pain in eye',
    'œil rouge': 'eye redness', 'yeux rouges': 'eye redness', 'rougeur des yeux': 'eye redness',
    'larmoiement': 'lacrimation', 'yeux qui coulent': 'lacrimation',
    'démangeaisons oculaires': 'itchiness of eye', 'yeux qui piquent': 'itchiness of eye',
    'yeux secs': 'itchiness of eye',
    'baisse de la vue': 'diminished vision', 'vision trouble': 'diminished vision',
    'vision floue': 'diminished vision', 'vision réduite': 'diminished vision',
    'vision double': 'double vision', 'diplopie': 'double vision',
    'cécité': 'blindness', 'perte de la vue': 'blindness',
    'fatigue oculaire': 'eye strain', 'yeux fatigués': 'eye strain',

    # ── Cardiovasculaire ──────────────────────────────────────────────────────
    'palpitations': 'palpitations', 'cœur qui bat fort': 'palpitations',
    'cœur qui s\'emballe': 'palpitations', 'tachycardie': 'increased heart rate',
    'rythme cardiaque rapide': 'increased heart rate', 'cœur rapide': 'increased heart rate',
    'bradycardie': 'decreased heart rate', 'cœur lent': 'decreased heart rate',
    'arythmie': 'irregular heartbeat', 'battements irréguliers': 'irregular heartbeat',

    # ── Neurologique / Mental ─────────────────────────────────────────────────
    'vertiges': 'dizziness', 'étourdissements': 'dizziness', 'etoudissements': 'dizziness',
    'tête qui tourne': 'dizziness', 'tete qui tourne': 'dizziness',
    'évanouissement': 'fainting', 'syncope': 'fainting', 'perte de connaissance': 'fainting',
    's\'évanouir': 'fainting', 'tomber dans les pommes': 'fainting',
    'insomnie': 'insomnia', 'troubles du sommeil': 'insomnia',
    'ne pas dormir': 'insomnia', 'difficile de dormir': 'insomnia',
    'somnolence': 'sleepiness', 'envie de dormir': 'sleepiness',
    'somnambulisme': 'sleepwalking',
    'anxiété': 'anxiety and nervousness', 'anxiete': 'anxiety and nervousness',
    'nervosité': 'anxiety and nervousness', 'angoisse': 'anxiety and nervousness',
    'stress': 'anxiety and nervousness', 'inquiet': 'anxiety and nervousness',
    'dépression': 'depression', 'depression': 'depression',
    'moral bas': 'depression', 'tristesse': 'depression',
    'convulsions': 'seizures', 'crise d\'épilepsie': 'seizures',
    'épilepsie': 'seizures', 'epilepsie': 'seizures',
    'paralysie': 'focal weakness', 'perte de sensation': 'loss of sensation',
    'engourdissement': 'loss of sensation', 'fourmillements': 'paresthesia',
    'picotements': 'paresthesia', 'paresthésies': 'paresthesia',
    'troubles de la mémoire': 'disturbance of memory', 'perte de mémoire': 'disturbance of memory',
    'hallucinations': 'delusions or hallucinations', 'délires': 'delusions or hallucinations',
    'agitation': 'restlessness', 'impossibilité de rester calme': 'restlessness',
    'troubles de l\'élocution': 'slurring words', 'difficulté à parler': 'slurring words',
    'dysarthrie': 'slurring words',

    # ── Urinaire ─────────────────────────────────────────────────────────────
    'mictions fréquentes': 'frequent urination', 'uriner souvent': 'frequent urination',
    'polyurie': 'frequent urination', 'urination fréquente': 'frequent urination',
    'brûlures urinaires': 'painful urination', 'douleur à la miction': 'painful urination',
    'miction douloureuse': 'painful urination', 'ça brûle quand j\'urine': 'painful urination',
    'sang dans les urines': 'blood in urine', 'hématurie': 'blood in urine',
    'urine rouge': 'blood in urine',
    'rétention urinaire': 'retention of urine', 'ne pas pouvoir uriner': 'retention of urine',
    'incontinence urinaire': 'involuntary urination', 'perte d\'urine': 'involuntary urination',
    'faible urine': 'low urine output', 'peu d\'urine': 'low urine output',
    'nycturie': 'excessive urination at night', 'uriner la nuit': 'excessive urination at night',

    # ── Transpiration / Frissons ──────────────────────────────────────────────
    'transpiration': 'sweating', 'sueurs': 'sweating',
    'sueurs nocturnes': 'sweating', 'transpirer': 'sweating',
    'sueurs froides': 'sweating', 'moite': 'sweating',
    'frissons': 'chills', 'avoir froid': 'chills', 'grelotter': 'chills',
    'bouffées de chaleur': 'flushing', 'bouffees de chaleur': 'flushing',
    'avoir chaud et froid': 'feeling hot and cold', 'chaud et froid': 'feeling hot and cold',
    'avoir chaud': 'feeling hot', 'sensation de chaleur': 'feeling hot',
    'avoir froid': 'feeling cold', 'sensation de froid': 'feeling cold',

    # ── Gonflement / Œdème ────────────────────────────────────────────────────
    'gonflement': 'peripheral edema', 'œdème': 'peripheral edema', 'oedeme': 'peripheral edema',
    'rétention d\'eau': 'fluid retention', 'rétention eau': 'fluid retention',
    'ganglions gonflés': 'swollen lymph nodes', 'ganglions': 'swollen lymph nodes',
    'adénopathie': 'swollen lymph nodes', 'ganglions enflés': 'swollen lymph nodes',
    'ventre gonflé': 'swollen abdomen', 'abdomen gonflé': 'swollen abdomen',

    # ── Généralités ───────────────────────────────────────────────────────────
    'faiblesse': 'weakness', 'faible': 'weakness',
    'douleur généralisée': 'ache all over', 'douleur partout': 'ache all over',
    'mal partout': 'ache all over', 'courbatures': 'ache all over',
    'douleur pelvienne': 'pelvic pain', 'pression pelvienne': 'pelvic pressure',
    'malaise': 'feeling ill', 'se sentir mal': 'feeling ill',
    'pas bien': 'feeling ill', 'syndrome grippal': 'flu-like syndrome',
    'grippe': 'flu-like syndrome',

    # ── Sanguins / Gynéco ─────────────────────────────────────────────────────
    'règles douloureuses': 'painful menstruation', 'dysménorrhée': 'painful menstruation',
    'règles abondantes': 'heavy menstrual flow', 'règles irrégulières': 'unpredictable menstruation',
    'absence de règles': 'absence of menstruation', 'aménorrhée': 'absence of menstruation',
    'pertes vaginales': 'vaginal discharge', 'écoulement vaginal': 'vaginal discharge',
    'démangeaisons vaginales': 'vaginal itching', 'douleur vaginale': 'vaginal pain',

    # ── Rash / Prurit ──────────────────────────────────────────────────────────
    'réaction allergique': 'allergic reaction', 'allergie': 'allergic reaction',
    'urticaire': 'skin rash', 'eczéma': 'skin rash',
    'peau rouge': 'skin rash', 'rougeur': 'skin rash',

    # ── Bouche / Dents ────────────────────────────────────────────────────────
    'mal aux dents': 'toothache', 'douleur dentaire': 'toothache',
    'aphte': 'mouth ulcer', 'ulcère buccal': 'mouth ulcer',
    'bouche sèche': 'mouth dryness', 'bouche seche': 'mouth dryness',
    'saignement des gencives': 'bleeding gums', 'gencives qui saignent': 'bleeding gums',
    'douleur aux gencives': 'pain in gums',

    # ── Divers ────────────────────────────────────────────────────────────────
    'congestion thoracique': 'congestion in chest', 'toux grasse': 'congestion in chest',
    'soif': 'thirst', 'soif excessive': 'thirst',
    'cauchemars': 'nightmares', 'troubles du goût': 'disturbance of smell or taste',
    'perte du goût': 'disturbance of smell or taste', 'perte de l\'odorat': 'disturbance of smell or taste',
    'anosmie': 'disturbance of smell or taste', 'agueusie': 'disturbance of smell or taste',
    'chute de cheveux': 'too little hair', 'perte de cheveux': 'too little hair',
    'alopécie': 'too little hair', 'calvitie': 'too little hair',
}


def _normalize_fr(text):
    """Normalise le texte français : minuscules + suppression des accents courants."""
    text = text.lower().strip()
    for old, new in [('é','e'),('è','e'),('ê','e'),('ë','e'),('à','a'),('â','a'),
                     ('ù','u'),('û','u'),('ü','u'),('î','i'),('ï','i'),
                     ('ô','o'),('ö','o'),('ç','c'),('œ','oe'),('æ','ae')]:
        text = text.replace(old, new)
    return text


# Index normalisé : clé sans accents → symptôme anglais (évite les bugs d'encodage)
_FR_TO_EN_NORMALIZED = {_normalize_fr(k): v for k, v in FR_TO_EN.items()}


def extract_symptoms_from_french(text):
    """Extrait les symptômes anglais depuis un texte français via correspondance de mots-clés.
    Utilisé comme fallback quand Groq n'est pas disponible."""
    normalized = _normalize_fr(text)
    found = {}
    # Trier par longueur décroissante pour favoriser les correspondances longues ("mal de tete" avant "tete")
    for fr_term in sorted(_FR_TO_EN_NORMALIZED, key=len, reverse=True):
        if fr_term in normalized:
            en_symptom = _FR_TO_EN_NORMALIZED[fr_term]
            if en_symptom not in found and en_symptom in features:
                found[en_symptom] = True
    return list(found.keys())

# Traduction Anglais → Français pour les maladies
EN_TO_FR_DISEASE = {
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
    # Maladies supplémentaires non traduites auparavant
    'kidney failure': 'Insuffisance rénale',
    'Kidney failure': 'Insuffisance rénale',
    'liver cancer': 'Cancer du foie',
    'Liver cancer': 'Cancer du foie',
    'marijuana abuse': 'Intoxication (substance)',
    'Marijuana abuse': 'Intoxication (substance)',
    'flu': 'Grippe', 'Flu': 'Grippe', 'Influenza': 'Grippe',
    'Sinusitis': 'Sinusite', 'sinusitis': 'Sinusite',
    'Bronchitis': 'Bronchite', 'bronchitis': 'Bronchite',
    'Upper respiratory infection': 'Infection respiratoire haute',
    'Anemia': 'Anémie', 'anemia': 'Anémie',
    'Appendicitis': 'Appendicite',
    'Pancreatitis': 'Pancréatite',
    'Sepsis': 'Sepsis', 'sepsis': 'Sepsis',
    'Meningitis': 'Méningite',
    'Stroke': 'AVC (Accident vasculaire cérébral)',
    'Epilepsy': 'Épilepsie',
    'Depression': 'Dépression',
    'Anxiety': 'Anxiété',
    'Obesity': 'Obésité',
    'Gout': 'Goutte',
    'Eczema': 'Eczéma',
    'Lupus': 'Lupus',
    'Celiac disease': 'Maladie cœliaque',
    'Irritable bowel syndrome': 'Syndrome de l\'intestin irritable',
    'Hypertensive heart disease': 'Cardiopathie hypertensive',
    'Renal failure': 'Insuffisance rénale',
    'Liver failure': 'Insuffisance hépatique',
    # Maladies retournées en minuscules par le modèle
    'common cold': 'Rhume commun',
    'breast infection (mastitis)': 'Infection mammaire (mastite)',
    'Breast infection (mastitis)': 'Infection mammaire (mastite)',
    'impulse control disorder': 'Trouble du contrôle des impulsions',
    'Impulse control disorder': 'Trouble du contrôle des impulsions',
    'chronic fatigue syndrome': 'Syndrome de fatigue chronique',
    'sleep apnea': 'Apnée du sommeil',
    'tension headache': 'Céphalées de tension',
    'cluster headache': 'Algie vasculaire de la face',
    'irritable bowel': 'Syndrome de l\'intestin irritable',
    'food poisoning': 'Intoxication alimentaire',
    'urinary tract infection': 'Infection urinaire',
    'strep throat': 'Angine streptococcique',
    'pink eye': 'Conjonctivite',
    'ear infection': 'Infection de l\'oreille',
    'intestinal obstruction': 'Occlusion intestinale',
    'Intestinal obstruction': 'Occlusion intestinale',
    'bowel obstruction': 'Occlusion intestinale',
    'gastric ulcer': 'Ulcère gastrique',
    'duodenal ulcer': 'Ulcère duodénal',
    'kidney stones': 'Calculs rénaux',
    'gallstones': 'Calculs biliaires',
    'cholecystitis': 'Cholécystite',
    'pneumothorax': 'Pneumothorax',
    'pulmonary embolism': 'Embolie pulmonaire',
    'deep vein thrombosis': 'Thrombose veineuse profonde',
    'cellulitis': 'Cellulite infectieuse',
    'scabies': 'Gale',
    'ringworm': 'Teigne',
    'shingles': 'Zona',
    'herpes': 'Herpès',
    'mumps': 'Oreillons',
    'measles': 'Rougeole',
    'rubella': 'Rubéole',
    'whooping cough': 'Coqueluche',
    'diphtheria': 'Diphtérie',
    'tetanus': 'Tétanos',
    'rabies': 'Rage',
    'leptospirosis': 'Leptospirose',
    'brucellosis': 'Brucellose',
    'cholera': 'Choléra',
    'dysentery': 'Dysenterie',
    'typhus': 'Typhus',
    'plague': 'Peste',
    'anthrax': 'Charbon',
    'leprosy': 'Lèpre',
    'sickle cell anemia': 'Drépanocytose',
    'thalassemia': 'Thalassémie',
    'hemophilia': 'Hémophilie',
    'leukemia': 'Leucémie',
    'lymphoma': 'Lymphome',
    'multiple myeloma': 'Myélome multiple',
    'colon cancer': 'Cancer du côlon',
    'lung cancer': 'Cancer du poumon',
    'breast cancer': 'Cancer du sein',
    'prostate cancer': 'Cancer de la prostate',
    'cervical cancer': 'Cancer du col de l\'utérus',
    'stomach cancer': 'Cancer de l\'estomac',
    'bladder cancer': 'Cancer de la vessie',
    'thyroid cancer': 'Cancer de la thyroïde',
    'skin cancer': 'Cancer de la peau',
    'melanoma': 'Mélanome',
    'ovarian cancer': 'Cancer des ovaires',
    'Gout': 'Goutte',
    'gout': 'Goutte',
}

model = None
encoder = None
features = []
intent_model = None

def train_model():
    print('[IA] Modèle absent — lancement de train.py (premier démarrage uniquement)...')
    subprocess.run([sys.executable, 'train.py'], check=True)
    print('[IA] Entraînement terminé.')

def load_model():
    global model, encoder, features, intent_model
    if not os.path.exists(MODEL_PATH):
        # En production Docker, le modèle est baked dans l'image via `RUN python train.py`.
        # Ce bloc ne s'exécute qu'en dev local si les fichiers .pkl sont absents.
        print('[IA] Fichiers de modèle introuvables — entraînement en cours...')
        train_model()

    try:
        model = joblib.load(MODEL_PATH)
        encoder = joblib.load(ENCODER_PATH)
        features = joblib.load(FEATURES_PATH)
        intent_model = joblib.load(INTENT_MODEL_PATH) if os.path.exists(INTENT_MODEL_PATH) else train_intents()

        print(f'Modele diagnostic charge: {len(encoder.classes_)} maladies')
        print(f'Liste des features chargee: {len(features)} symptomes')
    except Exception as e:
        print(f"Erreur lors du chargement des modeles: {e}")

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
        if not symptoms:
            symptoms = extract_symptoms_from_french(message)

    # Traduction FR→EN puis vérification que le symptôme existe dans les features
    input_symptoms_translated = []
    for s in symptoms:
        s_clean = s.lower().strip()
        en = FR_TO_EN.get(s_clean) or _FR_TO_EN_NORMALIZED.get(_normalize_fr(s_clean)) or s_clean
        if en in features:
            input_symptoms_translated.append(en)
        elif s_clean in features:
            input_symptoms_translated.append(s_clean)

    vector, final_symptoms = encode_patient_profile({'symptoms': input_symptoms_translated})
    probabilities = model.predict_proba(vector)[0]
    top_indices = np.argsort(probabilities)[-3:][::-1]

    suggestions = []
    for index in top_indices:
        confidence = float(probabilities[index]) * 100
        disease_en = encoder.classes_[index]
        disease_fr = (
            EN_TO_FR_DISEASE.get(disease_en)
            or EN_TO_FR_DISEASE.get(disease_en.lower())
            or EN_TO_FR_DISEASE.get(disease_en.title())
            or disease_en
        )

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
    clinic_context = data.get('context', '')
    audience = data.get('audience', 'staff')  # 'patient' (WhatsApp) ou 'staff' (chatbot interne)

    if not message:
        return jsonify({'intent': 'none', 'response': 'Bonjour !', 'reply': 'Bonjour !'})

    intent = predict_intent(message, intent_model)

    # Toujours tenter l'extraction de symptômes (LLM d'abord, puis matching FR)
    # Priorité : si des symptômes sont trouvés, on écrase l'intention du classificateur SVM
    extracted_symptoms = get_symptoms_via_llm(message)
    if not extracted_symptoms:
        extracted_symptoms = extract_symptoms_from_french(message)
    if extracted_symptoms:
            text = f"J'ai identifié les symptômes suivants : {', '.join(extracted_symptoms)}. Lancement de l'analyse..."
            return jsonify({
                'intent': 'ia_symptoms',
                'response': text,
                'reply': text,
                'symptoms': extracted_symptoms
            })

    smart_response = generate_smart_response(message, intent, clinic_context=clinic_context, audience=audience)
    return jsonify({
        'intent': intent,
        'response': smart_response,
        'reply': smart_response,
    })

@app.route('/symptoms', methods=['GET'])
def get_symptoms():
    return jsonify({'symptoms': features})


@app.route('/symptoms/fr', methods=['GET'])
def get_symptoms_fr():
    """Retourne le dictionnaire de traduction Français → Anglais pour le matching côté backend."""
    return jsonify({'fr_to_en': FR_TO_EN, 'fr_to_en_normalized': _FR_TO_EN_NORMALIZED})

if __name__ == '__main__':
    load_model()
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
