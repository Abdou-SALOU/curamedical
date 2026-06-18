"""
Script de données de démonstration — CuraMedical
Lance avec : docker-compose exec backend python seed_demo.py
             OU : python seed_demo.py (depuis le dossier backend)
"""
import os, django, sys
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curamedical.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.patients.models import Patient
from apps.appointments.models import RendezVous
from apps.consultations.models import Consultation
from apps.prescriptions.models import Prescription, LignePrescription

User = get_user_model()

print("🌱 Seeding demo data for CuraMedical…")

# ─────────────────────────────────────────────────────────────
# 1. Médecins (inclut le compte par défaut medecin/medecinpassword)
# ─────────────────────────────────────────────────────────────
MEDECINS_DATA = [
    # Compte par défaut du README — conserve son mot de passe original
    {'username': 'medecin',      'first_name': 'Nouridine', 'last_name': 'Sawadogo', 'email': 'medecin@CuraMedical.com',     'password': 'medecinpassword'},
    # Comptes démo
    {'username': 'dr.amrani',    'first_name': 'Sara',   'last_name': 'Amrani',    'email': 's.amrani@curamedical.io',     'password': 'Demo2026!'},
    {'username': 'dr.hakimi',    'first_name': 'Mehdi',  'last_name': 'Hakimi',    'email': 'm.hakimi@curamedical.io',     'password': 'Demo2026!'},
    {'username': 'dr.bennis',    'first_name': 'Leila',  'last_name': 'Bennis',    'email': 'l.bennis@curamedical.io',     'password': 'Demo2026!'},
    {'username': 'dr.cherkaoui', 'first_name': 'Omar',   'last_name': 'Cherkaoui', 'email': 'o.cherkaoui@curamedical.io', 'password': 'Demo2026!'},
]

medecins = []
for d in MEDECINS_DATA:
    u, created = User.objects.get_or_create(username=d['username'])
    u.set_password(d['password'])
    u.first_name = d['first_name']
    u.last_name  = d['last_name']
    u.email      = d['email']
    u.role       = 'medecin'
    u.is_staff   = True
    u.save()
    medecins.append(u)
    print(f"  {'✓ Créé' if created else '→ Mis à jour'} médecin : Dr. {d['last_name']}")

# medecins[0] = medecin (Benali), [1] = Amrani, [2] = Hakimi, [3] = Bennis, [4] = Cherkaoui

# Secrétaire par défaut (conserve son mot de passe)
sec, _ = User.objects.get_or_create(username='secretaire')
sec.set_password('secretairepassword')
sec.first_name = 'Nadia'
sec.last_name  = 'Tahiri'
sec.email      = 'secretaire@CuraMedical.com'
sec.role       = 'secretaire'
sec.is_staff   = True
sec.save()
print(f"  → Secrétaire : {sec.username}")

# Secrétaire démo
sec2, _ = User.objects.get_or_create(username='secretaire.demo')
sec2.set_password('Demo2026!')
sec2.first_name = 'Samira'
sec2.last_name  = 'Idrissi'
sec2.email      = 'n.tahiri@curamedical.io'
sec2.role       = 'secretaire'
sec2.is_staff   = True
sec2.save()

# ─────────────────────────────────────────────────────────────
# 2. Patients
# ─────────────────────────────────────────────────────────────
PATIENTS_DATA = [
    {'prenom': 'Khalil',       'nom': 'Bensalem',   'date_naissance': '1970-03-15', 'sexe': 'M', 'cin': 'BE123456', 'telephone': '+212661234567', 'email': 'k.bensalem@email.ma',  'groupe_sanguin': 'A+',  'allergies': 'Pénicilline',       'antecedents_medicaux': 'Hypertension artérielle depuis 2018, tabagisme arrêté 2020'},
    {'prenom': 'Amina',        'nom': 'Tazi',        'date_naissance': '1988-07-22', 'sexe': 'F', 'cin': 'TA654321', 'telephone': '+212662891023', 'email': 'a.tazi@email.ma',       'groupe_sanguin': 'O+',  'allergies': '',                  'antecedents_medicaux': 'Première visite'},
    {'prenom': 'Youssef',      'nom': 'El Idrissi',  'date_naissance': '1957-11-08', 'sexe': 'M', 'cin': 'EI789012', 'telephone': '+212663442119', 'email': 'y.elidrissi@email.ma',  'groupe_sanguin': 'B+',  'allergies': 'Aspirine',          'antecedents_medicaux': 'Diabète type 2 depuis 2015, dyslipidémie'},
    {'prenom': 'Fatima Zahra', 'nom': 'Lahlou',      'date_naissance': '1995-04-30', 'sexe': 'F', 'cin': 'LA345678', 'telephone': '+212664778902', 'email': 'fz.lahlou@email.ma',    'groupe_sanguin': 'AB-', 'allergies': 'Iode',              'antecedents_medicaux': 'Migraines chroniques'},
    {'prenom': 'Omar',         'nom': 'Cherkaoui',   'date_naissance': '1979-09-12', 'sexe': 'M', 'cin': 'CH901234', 'telephone': '+212665003451', 'email': 'o.cherkaoui@email.ma',  'groupe_sanguin': 'O-',  'allergies': '',                  'antecedents_medicaux': 'Lombalgie chronique L4-L5, hernie discale 2021'},
    {'prenom': 'Salma',        'nom': 'Bennani',     'date_naissance': '1991-01-25', 'sexe': 'F', 'cin': 'BE567890', 'telephone': '+212666221779', 'email': 's.bennani@email.ma',    'groupe_sanguin': 'A-',  'allergies': 'Latex, Pollen',     'antecedents_medicaux': "Asthme persistant léger depuis l'enfance"},
    {'prenom': 'Hamid',        'nom': 'Moussaoui',   'date_naissance': '1965-06-03', 'sexe': 'M', 'cin': 'MO112233', 'telephone': '+212667334455', 'email': 'h.moussaoui@email.ma',  'groupe_sanguin': 'B-',  'allergies': '',                  'antecedents_medicaux': 'Insuffisance coronarienne, pontage 2019'},
    {'prenom': 'Zineb',        'nom': 'Alaoui',      'date_naissance': '2000-12-18', 'sexe': 'F', 'cin': 'AL445566', 'telephone': '+212668556677', 'email': 'z.alaoui@email.ma',     'groupe_sanguin': 'O+',  'allergies': 'Arachides',         'antecedents_medicaux': ''},
    {'prenom': 'Rachid',       'nom': 'Bensouda',    'date_naissance': '1952-08-27', 'sexe': 'M', 'cin': 'BS778899', 'telephone': '+212669112233', 'email': 'r.bensouda@email.ma',   'groupe_sanguin': 'A+',  'allergies': 'Sulfamides',        'antecedents_medicaux': 'BPCO, tabagisme actif, insuffisance respiratoire'},
    {'prenom': 'Houda',        'nom': 'Mansouri',    'date_naissance': '1983-02-14', 'sexe': 'F', 'cin': 'MA334455', 'telephone': '+212660998877', 'email': 'h.mansouri@email.ma',   'groupe_sanguin': 'AB+', 'allergies': '',                  'antecedents_medicaux': 'Hypothyroïdie, traitement substitutif depuis 2019'},
    {'prenom': 'Karim',        'nom': 'Berrada',     'date_naissance': '1975-05-09', 'sexe': 'M', 'cin': 'BE556677', 'telephone': '+212661223344', 'email': 'k.berrada@email.ma',    'groupe_sanguin': 'O+',  'allergies': '',                  'antecedents_medicaux': 'Hypertension, obésité IMC 32'},
    {'prenom': 'Nadia',        'nom': 'El Fassi',    'date_naissance': '1993-10-01', 'sexe': 'F', 'cin': 'EF889900', 'telephone': '+212662445566', 'email': 'n.elfassi@email.ma',    'groupe_sanguin': 'B+',  'allergies': 'Aspirine, AINS',    'antecedents_medicaux': 'Gastrite chronique, ulcère traité 2022'},
    {'prenom': 'Mourad',       'nom': 'Chraibi',     'date_naissance': '1960-04-18', 'sexe': 'M', 'cin': 'CR667788', 'telephone': '+212663551122', 'email': 'm.chraibi@email.ma',    'groupe_sanguin': 'A-',  'allergies': '',                  'antecedents_medicaux': 'Insuffisance rénale chronique stade 3'},
    {'prenom': 'Leila',        'nom': 'Bouhsain',    'date_naissance': '1985-08-05', 'sexe': 'F', 'cin': 'BH223344', 'telephone': '+212664889900', 'email': 'l.bouhsain@email.ma',   'groupe_sanguin': 'O-',  'allergies': 'Sulfamides',        'antecedents_medicaux': 'Lupus érythémateux systémique depuis 2017'},
]

patients = []
for p in PATIENTS_DATA:
    patient, created = Patient.objects.get_or_create(cin=p['cin'], defaults=p)
    if not created:
        for k, v in p.items():
            setattr(patient, k, v)
        patient.save()
    patients.append(patient)
    print(f"  {'✓' if created else '→'} Patient : {p['prenom']} {p['nom']}")

# ─────────────────────────────────────────────────────────────
# 3. Rendez-vous — répartis sur 5 mois pour les graphiques
#    delta_days négatifs → passé | 0 → aujourd'hui | positifs → futur
#    medecins[0]=Benali(defaut), [1]=Amrani, [2]=Hakimi, [3]=Bennis, [4]=Cherkaoui
# ─────────────────────────────────────────────────────────────
now = timezone.now()

APPOINTMENTS = [
    # ── Janvier (≈ -120 à -105 jours) ─────────────────────────
    {'patient': patients[0],  'medecin': medecins[1], 'delta': -120, 'h': 9,  'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Bilan cardiaque annuel — hypertension'},
    {'patient': patients[2],  'medecin': medecins[2], 'delta': -118, 'h': 10, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Contrôle diabète type 2'},
    {'patient': patients[6],  'medecin': medecins[1], 'delta': -115, 'h': 14, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Suivi post-pontage — ECG de contrôle'},
    {'patient': patients[10], 'medecin': medecins[0], 'delta': -112, 'h': 11, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Suivi hypertension — ajustement traitement'},
    {'patient': patients[3],  'medecin': medecins[4], 'delta': -110, 'h': 16, 'statut': 'ANNULE',   'type': 'EN_LIGNE',   'motif': 'Suivi migraines'},
    # ── Février (≈ -90 à -75 jours) ───────────────────────────
    {'patient': patients[5],  'medecin': medecins[3], 'delta': -90,  'h': 9,  'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Bilan asthme — spirométrie hivernale'},
    {'patient': patients[8],  'medecin': medecins[2], 'delta': -88,  'h': 15, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'BPCO — évaluation fonctionnelle respiratoire'},
    {'patient': patients[9],  'medecin': medecins[4], 'delta': -85,  'h': 10, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Hypothyroïdie — dosage TSH'},
    {'patient': patients[12], 'medecin': medecins[0], 'delta': -82,  'h': 14, 'statut': 'TERMINE',  'type': 'EN_LIGNE',   'motif': 'Suivi insuffisance rénale — créatinine'},
    {'patient': patients[1],  'medecin': medecins[2], 'delta': -80,  'h': 11, 'statut': 'ANNULE',   'type': 'PRESENTIEL', 'motif': 'Consultation de bilan général'},
    # ── Mars (≈ -65 à -50 jours) ──────────────────────────────
    {'patient': patients[4],  'medecin': medecins[3], 'delta': -65,  'h': 14, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Lombalgie — contrôle post-infiltration'},
    {'patient': patients[0],  'medecin': medecins[1], 'delta': -63,  'h': 9,  'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Suivi tension — bilan sanguin'},
    {'patient': patients[13], 'medecin': medecins[3], 'delta': -60,  'h': 10, 'statut': 'TERMINE',  'type': 'EN_LIGNE',   'motif': 'Lupus — bilan immunologique'},
    {'patient': patients[11], 'medecin': medecins[2], 'delta': -58,  'h': 16, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Gastrite — fibroscopie digestive'},
    {'patient': patients[7],  'medecin': medecins[0], 'delta': -55,  'h': 11, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Bilan annuel — prise de sang'},
    {'patient': patients[2],  'medecin': medecins[2], 'delta': -52,  'h': 9,  'statut': 'ANNULE',   'type': 'PRESENTIEL', 'motif': 'Contrôle glycémie HbA1c'},
    # ── Avril (≈ -45 à -15 jours) ─────────────────────────────
    {'patient': patients[6],  'medecin': medecins[1], 'delta': -45,  'h': 8,  'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Contrôle post-pontage — échocardiographie'},
    {'patient': patients[9],  'medecin': medecins[4], 'delta': -42,  'h': 10, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Hypothyroïdie — renouvellement ordonnance'},
    {'patient': patients[3],  'medecin': medecins[4], 'delta': -38,  'h': 17, 'statut': 'TERMINE',  'type': 'EN_LIGNE',   'motif': 'Suivi migraines — résultats IRM'},
    {'patient': patients[5],  'medecin': medecins[3], 'delta': -35,  'h': 11, 'statut': 'TERMINE',  'type': 'EN_LIGNE',   'motif': 'Asthme printanier — ajustement corticoïdes'},
    {'patient': patients[10], 'medecin': medecins[0], 'delta': -32,  'h': 15, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Suivi hypertension et obésité'},
    {'patient': patients[12], 'medecin': medecins[0], 'delta': -28,  'h': 10, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Insuffisance rénale — suivi néphrologue'},
    {'patient': patients[8],  'medecin': medecins[2], 'delta': -25,  'h': 9,  'statut': 'ANNULE',   'type': 'PRESENTIEL', 'motif': 'BPCO — kinésithérapie respiratoire'},
    # ── Mai passé (≈ -14 à -1 jours) ─────────────────────────
    {'patient': patients[0],  'medecin': medecins[1], 'delta': -14,  'h': 9,  'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Suivi hypertension — bilan cardiaque'},
    {'patient': patients[2],  'medecin': medecins[2], 'delta': -10,  'h': 10, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Contrôle diabète type 2 — ajustement traitement'},
    {'patient': patients[4],  'medecin': medecins[1], 'delta': -7,   'h': 14, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Lombalgie aiguë — examen clinique'},
    {'patient': patients[5],  'medecin': medecins[3], 'delta': -5,   'h': 11, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Suivi asthme — spirométrie'},
    {'patient': patients[6],  'medecin': medecins[1], 'delta': -3,   'h': 8,  'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Contrôle post-pontage — ECG'},
    {'patient': patients[8],  'medecin': medecins[2], 'delta': -2,   'h': 15, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'BPCO — évaluation fonctionnelle respiratoire'},
    {'patient': patients[9],  'medecin': medecins[4], 'delta': -1,   'h': 16, 'statut': 'TERMINE',  'type': 'PRESENTIEL', 'motif': 'Hypothyroïdie — dosage TSH'},
    {'patient': patients[1],  'medecin': medecins[2], 'delta': -6,   'h': 9,  'statut': 'TERMINE',  'type': 'EN_LIGNE',   'motif': 'Première consultation — bilan général'},
    {'patient': patients[3],  'medecin': medecins[4], 'delta': -4,   'h': 17, 'statut': 'TERMINE',  'type': 'EN_LIGNE',   'motif': 'Suivi migraines — ajustement traitement'},
    # ── Aujourd'hui ───────────────────────────────────────────
    {'patient': patients[0],  'medecin': medecins[0], 'delta': 0,    'h': 8,  'statut': 'CONFIRME', 'type': 'PRESENTIEL', 'motif': 'Suivi tension artérielle',                    'duree': 30},
    {'patient': patients[1],  'medecin': medecins[2], 'delta': 0,    'h': 9,  'statut': 'CONFIRME', 'type': 'EN_LIGNE',   'motif': 'Consultation de suivi',                        'duree': 45},
    {'patient': patients[2],  'medecin': medecins[1], 'delta': 0,    'h': 10, 'statut': 'EN_COURS', 'type': 'PRESENTIEL', 'motif': 'Contrôle glycémie et hémoglobine glyquée',     'duree': 30},
    {'patient': patients[4],  'medecin': medecins[3], 'delta': 0,    'h': 11, 'statut': 'PLANIFIE', 'type': 'PRESENTIEL', 'motif': 'Douleurs lombaires — infiltration',             'duree': 60},
    {'patient': patients[7],  'medecin': medecins[2], 'delta': 0,    'h': 14, 'statut': 'PLANIFIE', 'type': 'PRESENTIEL', 'motif': 'Bilan annuel',                                  'duree': 30},
    {'patient': patients[10], 'medecin': medecins[0], 'delta': 0,    'h': 15, 'statut': 'CONFIRME', 'type': 'EN_LIGNE',   'motif': 'Suivi hypertension et poids',                  'duree': 30},
    {'patient': patients[13], 'medecin': medecins[3], 'delta': 0,    'h': 16, 'statut': 'DEMANDE',  'type': 'PRESENTIEL', 'motif': 'Lupus — douleurs articulaires aiguës',         'duree': 45},
    # ── Futurs ────────────────────────────────────────────────
    {'patient': patients[5],  'medecin': medecins[3], 'delta': 2,    'h': 9,  'statut': 'CONFIRME', 'type': 'EN_LIGNE',   'motif': 'Suivi asthme printanier',                      'duree': 30},
    {'patient': patients[3],  'medecin': medecins[4], 'delta': 3,    'h': 10, 'statut': 'PLANIFIE', 'type': 'PRESENTIEL', 'motif': 'IRM cérébrale — résultats migraines',           'duree': 60},
    {'patient': patients[6],  'medecin': medecins[1], 'delta': 5,    'h': 8,  'statut': 'CONFIRME', 'type': 'PRESENTIEL', 'motif': 'Échocardiographie de contrôle',                 'duree': 60},
    {'patient': patients[9],  'medecin': medecins[2], 'delta': 7,    'h': 11, 'statut': 'PLANIFIE', 'type': 'PRESENTIEL', 'motif': 'Renouvellement ordonnance thyroïde',            'duree': 20},
    {'patient': patients[11], 'medecin': medecins[2], 'delta': 8,    'h': 14, 'statut': 'DEMANDE',  'type': 'PRESENTIEL', 'motif': 'Douleurs épigastriques persistantes',           'duree': 30},
    {'patient': patients[8],  'medecin': medecins[2], 'delta': 10,   'h': 9,  'statut': 'PLANIFIE', 'type': 'EN_LIGNE',   'motif': 'Suivi BPCO — résultats spirométrie',            'duree': 45},
    {'patient': patients[12], 'medecin': medecins[0], 'delta': 12,   'h': 10, 'statut': 'PLANIFIE', 'type': 'PRESENTIEL', 'motif': 'Insuffisance rénale — suivi trimestriel',       'duree': 30},
]

rdvs = []
for a in APPOINTMENTS:
    dt = now.replace(hour=a['h'], minute=0, second=0, microsecond=0) + timedelta(days=a['delta'])
    rdv, created = RendezVous.objects.get_or_create(
        patient=a['patient'], medecin=a['medecin'], date_heure=dt,
        defaults={
            'statut':            a['statut'],
            'type_consultation': a['type'],
            'motif':             a['motif'],
            'duree':             a.get('duree', 30),
        }
    )
    if not created:
        rdv.statut = a['statut']
        rdv.save(update_fields=['statut'])
    rdvs.append({'rdv': rdv, 'statut': a['statut'], 'dt': dt})
    sign = '+' if a['delta'] >= 0 else ''
    print(f"  {'✓' if created else '→'} RDV : {a['patient'].prenom} {a['patient'].nom} → Dr. {a['medecin'].last_name} J{sign}{a['delta']}")

# ─────────────────────────────────────────────────────────────
# 4. Consultations (pour les RDV terminés)
#    symptomes : texte libre en français (pas de liste Python)
#    date_consultation : forcée à la date du RDV via .update()
# ─────────────────────────────────────────────────────────────
CONSULTATIONS = [
    # rdv_idx pointe sur l'index dans APPOINTMENTS
    # Janvier
    {
        'rdv_idx': 0,
        'symptomes': 'Céphalées matinales, vertiges, palpitations, essoufflement à l\'effort',
        'examen': 'TA 165/98 mmHg, FC 88 bpm, auscultation cardio normale, pas d\'œdème.',
        'diagnostic': 'Hypertension artérielle stade 2 mal contrôlée',
        'notes': 'Renforcement du traitement antihypertenseur. Régime hyposodé strict. Contrôle dans 4 semaines.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Hypertension artérielle', 'confidence': 0.92}, {'disease': 'Insuffisance cardiaque débutante', 'confidence': 0.34}],
    },
    {
        'rdv_idx': 1,
        'symptomes': 'Fatigue intense, amaigrissement, polydipsie, polyurie, perte d\'appétit',
        'examen': 'Glycémie à jeun 2.4 g/L, HbA1c 9.2%, examen des pieds normal.',
        'diagnostic': 'Diabète type 2 déséquilibré',
        'notes': 'Ajustement metformine + ajout insuline basale. Éducation thérapeutique programmée.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Diabète type 2', 'confidence': 0.87}, {'disease': 'Hyperglycémie chronique', 'confidence': 0.65}],
    },
    {
        'rdv_idx': 2,
        'symptomes': 'Douleurs thoraciques à l\'effort, dyspnée d\'effort, fatigue chronique',
        'examen': 'ECG : rythme sinusal, pas de trouble de repolarisation. TA 130/80. Cicatrice de sternotomie stable.',
        'diagnostic': 'Post-pontage aorto-coronarien — évolution favorable',
        'notes': 'Poursuite du traitement antiagrégant et statine. Réhabilitation cardiaque à maintenir.',
        'ia': False,
        'ia_suggestions': [],
    },
    {
        'rdv_idx': 3,
        'symptomes': 'Œdèmes des membres inférieurs, nausées, fatigue, maux de tête',
        'examen': 'Créatinine 185 µmol/L, DFG 38 mL/min, protéinurie 0.6 g/24h.',
        'diagnostic': 'Insuffisance rénale chronique stade 3B — aggravation légère',
        'notes': 'Restriction sodée et protéique. Néphrologue recommandé. Bilan dans 3 mois.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Insuffisance rénale chronique', 'confidence': 0.89}, {'disease': 'Syndrome néphrotique', 'confidence': 0.28}],
    },
    # Février
    {
        'rdv_idx': 5,
        'symptomes': 'Toux sèche nocturne, dyspnée au repos, sifflements thoraciques, oppression thoracique',
        'examen': 'Spirométrie : VEMS/CV = 74%, DEP 68% théorique. Auscultation : sibilances bilatérales.',
        'diagnostic': 'Asthme persistant léger — légère décompensation saisonnière',
        'notes': 'Augmentation corticoïdes inhalés. Bronchodilatateur de secours. Éviter allergènes.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Asthme bronchique', 'confidence': 0.84}, {'disease': 'BPCO', 'confidence': 0.21}],
    },
    {
        'rdv_idx': 6,
        'symptomes': 'Dyspnée au moindre effort, toux productive, expectoration purulente, fatigue extrême',
        'examen': 'EFR : VEMS 58% théorique, syndrome obstructif sévère. SaO2 94% au repos.',
        'diagnostic': 'BPCO stade GOLD III avec exacerbation légère',
        'notes': 'Corticoïde systémique 5 jours. Kinésithérapie respiratoire. Consultation pneumologue.',
        'ia': True,
        'ia_suggestions': [{'disease': 'BPCO exacerbée', 'confidence': 0.81}, {'disease': 'Insuffisance respiratoire', 'confidence': 0.44}],
    },
    {
        'rdv_idx': 7,
        'symptomes': 'Fatigue chronique, frilosité, prise de poids, ralentissement intellectuel, constipation',
        'examen': 'TSH 0.12 mUI/L (normale 0.4-4.0), T4L élevée. Pas de signe d\'hyperthyroïdie clinique.',
        'diagnostic': 'Hypothyroïdie sous-traitée — dose lévothyroxine insuffisante',
        'notes': 'Augmentation lévothyroxine de 75 à 100 mcg. Contrôle TSH dans 6 semaines.',
        'ia': False,
        'ia_suggestions': [],
    },
    {
        'rdv_idx': 8,
        'symptomes': 'Œdèmes, douleurs lombaires, asthénie, protéinurie à la bandelette',
        'examen': 'Créatinine 195 µmol/L, potassium 5.4 mEq/L, DFG 35 mL/min.',
        'diagnostic': 'Insuffisance rénale chronique stade 3B — progression',
        'notes': 'Orientation urgente vers néphrologue. Restriction protéique renforcée.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Insuffisance rénale chronique', 'confidence': 0.91}, {'disease': 'Glomérulopathie', 'confidence': 0.32}],
    },
    # Mars
    {
        'rdv_idx': 10,
        'symptomes': 'Douleurs lombaires irradiant dans le membre inférieur droit, contractures, paresthésies',
        'examen': 'Douleur lombaire L4-L5 à la palpation, contracture paravertébrale, Lasègue positif à 45°.',
        'diagnostic': 'Lombalgie aiguë sur hernie discale L4-L5',
        'notes': 'AINS + myorelaxant 10 jours. Kinésithérapie prescrite. Arrêt travail 7 jours.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Lombalgie discale', 'confidence': 0.78}, {'disease': 'Sciatique L5', 'confidence': 0.55}],
    },
    {
        'rdv_idx': 11,
        'symptomes': 'Céphalées persistantes, vertiges posturaux, bourdonnements d\'oreilles',
        'examen': 'TA 158/95 mmHg, FC 76 bpm. Fond d\'œil : artérioles rétrécies.',
        'diagnostic': 'Hypertension artérielle stade 2 — retentissement oculaire',
        'notes': 'Adaptation traitement. Avis ophtalmologue recommandé. Contrôle dans 3 semaines.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Hypertension artérielle', 'confidence': 0.90}, {'disease': 'Rétinopathie hypertensive', 'confidence': 0.48}],
    },
    {
        'rdv_idx': 12,
        'symptomes': 'Érythème malaire, arthralgies, fatigue, fièvre intermittente, chute de cheveux',
        'examen': 'ANA positifs 1/320, anti-ADN natifs élevés. Complément C3 bas. Pas d\'atteinte rénale.',
        'diagnostic': 'Lupus érythémateux systémique — poussée modérée',
        'notes': 'Augmentation hydroxychloroquine. Avis rhumatologue urgent. Photoprotection stricte.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Lupus érythémateux systémique', 'confidence': 0.85}, {'disease': 'Syndrome de Sjögren', 'confidence': 0.29}],
    },
    {
        'rdv_idx': 13,
        'symptomes': 'Douleurs épigastriques post-prandiales, brûlures, nausées, régurgitations acides',
        'examen': 'Fibroscopie : muqueuse gastrique érythémateuse, pas d\'ulcère actif. HP négatif.',
        'diagnostic': 'Gastrite chronique — en rémission',
        'notes': 'Poursuite IPP 4 semaines. Régime sans irritants. Réévaluation dans 2 mois.',
        'ia': False,
        'ia_suggestions': [],
    },
    {
        'rdv_idx': 14,
        'symptomes': 'Fatigue, céphalées légères, manque d\'énergie',
        'examen': 'Examen général normal. PA 120/75 mmHg. IMC 22.4. Biologie normale.',
        'diagnostic': 'Syndrome anxio-dépressif. Bilan initial normal.',
        'notes': 'Bilan biologique prescrit. Suivi mensuel. Orientation vers médecin traitant.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Syndrome anxieux', 'confidence': 0.61}, {'disease': 'Anémie', 'confidence': 0.38}],
    },
    # Avril
    {
        'rdv_idx': 16,
        'symptomes': 'Douleurs thoraciques à l\'effort, dyspnée, palpitations irrégulières',
        'examen': 'Échocardiographie : FE 55%, dilatation OG légère. Pas d\'épanchement péricardique.',
        'diagnostic': 'Post-pontage aorto-coronarien — FE conservée, surveillance rapprochée',
        'notes': 'Maintien bithérapie antiagrégante. Bêtabloquant maintenu. Prochain bilan dans 6 mois.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Insuffisance cardiaque débutante', 'confidence': 0.45}, {'disease': 'Fibrillation auriculaire', 'confidence': 0.30}],
    },
    {
        'rdv_idx': 17,
        'symptomes': 'Asthénie persistante, frilosité, prise de poids légère',
        'examen': 'TSH normalisée à 1.8 mUI/L sous lévothyroxine 100 mcg. T4L normale.',
        'diagnostic': 'Hypothyroïdie — bonne réponse au traitement',
        'notes': 'Poursuite lévothyroxine 100 mcg. Prochain contrôle TSH dans 6 mois.',
        'ia': False,
        'ia_suggestions': [],
    },
    {
        'rdv_idx': 18,
        'symptomes': 'Céphalées hémicrâniques pulsatiles, nausées, photophobie, phonophobie, aura visuelle',
        'examen': 'IRM cérébrale : normale. Pas de lésion vasculaire. Examen neurologique normal.',
        'diagnostic': 'Migraine avec aura — épisode aigu',
        'notes': 'Triptan prescrit pour crises aiguës. Propranolol en traitement de fond. Éviction facteurs déclenchants.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Migraine avec aura', 'confidence': 0.88}, {'disease': 'Céphalée de tension', 'confidence': 0.32}],
    },
    {
        'rdv_idx': 19,
        'symptomes': 'Toux sèche nocturne, dyspnée légère, nez qui coule, yeux qui piquent',
        'examen': 'Spirométrie stable. DEP 72% théorique. Légère rhino-conjonctivite allergique.',
        'diagnostic': 'Asthme léger — exacerbation printanière allergique',
        'notes': 'Augmentation temporaire corticoïdes inhalés. Antihistaminique ajouté. Éviter sorties au vent.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Asthme allergique', 'confidence': 0.82}, {'disease': 'Rhinite allergique', 'confidence': 0.70}],
    },
    {
        'rdv_idx': 20,
        'symptomes': 'Vertiges, maux de tête matinaux, essoufflement à la montée des escaliers, palpitations',
        'examen': 'TA 160/95 mmHg, FC 82 bpm. IMC 33.4. Bilan lipidique : LDL 1.6 g/L.',
        'diagnostic': 'Hypertension artérielle mal contrôlée — obésité associée',
        'notes': 'Ajout IEC au traitement. Consultation diététicienne. Activité physique adaptée recommandée.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Hypertension artérielle', 'confidence': 0.91}, {'disease': 'Syndrome métabolique', 'confidence': 0.60}],
    },
    {
        'rdv_idx': 21,
        'symptomes': 'Œdèmes des chevilles, douleurs lombaires basses, oligurie légère',
        'examen': 'Créatinine 210 µmol/L (aggravation), DFG 30 mL/min. Protéinurie 0.9 g/24h.',
        'diagnostic': 'Insuffisance rénale chronique stade 3B — aggravation nette',
        'notes': 'Orientation néphrologue en urgence relative. Préparation pour suppléance à discuter.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Insuffisance rénale chronique', 'confidence': 0.93}, {'disease': 'Néphropathie diabétique', 'confidence': 0.38}],
    },
    # Mai passé
    {
        'rdv_idx': 23,
        'symptomes': 'Céphalées matinales, vertiges, palpitations, essoufflement à l\'effort',
        'examen': 'TA 158/92 mmHg, FC 84 bpm, auscultation cardio normale.',
        'diagnostic': 'Hypertension artérielle stade 2 — contrôle partiel',
        'notes': 'Renforcement du traitement. Sel < 5g/j. Contrôle dans 4 semaines.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Hypertension artérielle', 'confidence': 0.93}, {'disease': 'Insuffisance cardiaque débutante', 'confidence': 0.28}],
    },
    {
        'rdv_idx': 24,
        'symptomes': 'Polyurie, polydipsie, fatigue, glycémie capillaire élevée à domicile',
        'examen': 'Glycémie 2.1 g/L, HbA1c 8.8%, pieds normaux.',
        'diagnostic': 'Diabète type 2 — contrôle insuffisant',
        'notes': 'Augmentation insuline basale. Autosurveillance renforcée. Diététicienne recommandée.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Diabète type 2', 'confidence': 0.90}, {'disease': 'Hyperglycémie chronique', 'confidence': 0.68}],
    },
    {
        'rdv_idx': 25,
        'symptomes': 'Douleurs lombaires irradiant dans la jambe droite, paresthésies, contractures',
        'examen': 'Contracture paravertébrale L4-L5, Lasègue positif à 50°.',
        'diagnostic': 'Lombalgie aiguë sur hernie discale L4-L5',
        'notes': 'AINS + myorelaxant 10 jours. Kinésithérapie prescrite. Arrêt travail 7 jours.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Lombalgie discale', 'confidence': 0.80}, {'disease': 'Sciatique L5', 'confidence': 0.52}],
    },
    {
        'rdv_idx': 26,
        'symptomes': 'Toux sèche nocturne, sifflements, dyspnée d\'effort',
        'examen': 'Spirométrie : VEMS/CV = 73%, DEP 70% théorique.',
        'diagnostic': 'Asthme persistant léger — contrôle partiel',
        'notes': 'Augmentation corticoïdes inhalés. Éducation sur technique d\'inhalation.',
        'ia': False,
        'ia_suggestions': [],
    },
    {
        'rdv_idx': 27,
        'symptomes': 'Douleurs thoraciques à l\'effort, fatigue, dyspnée',
        'examen': 'ECG : rythme sinusal. TA 128/78. Cicatrice de sternotomie stable.',
        'diagnostic': 'Post-pontage aorto-coronarien — évolution stable',
        'notes': 'Poursuite traitement. Prochaine échocardiographie dans 6 mois.',
        'ia': False,
        'ia_suggestions': [],
    },
    {
        'rdv_idx': 28,
        'symptomes': 'Dyspnée au moindre effort, toux productive, fièvre légère à 38.2°C',
        'examen': 'EFR : VEMS 55% théorique. SaO2 92% à l\'effort. Auscultation : ronchi bilatéraux.',
        'diagnostic': 'BPCO stade GOLD III — exacerbation infectieuse',
        'notes': 'Antibiothérapie + corticoïde systémique. Kinésithérapie respiratoire urgente.',
        'ia': True,
        'ia_suggestions': [{'disease': 'BPCO exacerbée', 'confidence': 0.85}, {'disease': 'Pneumonie', 'confidence': 0.40}],
    },
    {
        'rdv_idx': 29,
        'symptomes': 'Fatigue, frilosité, prise de poids, ralentissement cognitif',
        'examen': 'TSH 4.8 mUI/L, T4L légèrement basse.',
        'diagnostic': 'Hypothyroïdie — légère sous-compensation',
        'notes': 'Majoration légère lévothyroxine. Contrôle TSH dans 6 semaines.',
        'ia': False,
        'ia_suggestions': [],
    },
    {
        'rdv_idx': 30,
        'symptomes': 'Fatigue, céphalées, palpitations, anxiété généralisée',
        'examen': 'Examen général normal. PA 118/72 mmHg. Biologie normale.',
        'diagnostic': 'Syndrome anxio-dépressif — première consultation',
        'notes': 'Bilan biologique complet. Suivi mensuel. Psychologue recommandé.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Syndrome anxieux', 'confidence': 0.64}, {'disease': 'Dépression légère', 'confidence': 0.42}],
    },
    {
        'rdv_idx': 31,
        'symptomes': 'Céphalées hémicrâniques, nausées, vomissements, photophobie',
        'examen': 'Examen neurologique normal. Fond d\'œil normal. Pas de signe méningé.',
        'diagnostic': 'Migraine sans aura — épisode aigu',
        'notes': 'Triptan prescrit pour crises aiguës. Propranolol en traitement de fond.',
        'ia': True,
        'ia_suggestions': [{'disease': 'Migraine', 'confidence': 0.88}, {'disease': 'Céphalée de tension', 'confidence': 0.32}],
    },
]

consults_created = []
consults_map = {}  # rdv_idx → consultation

for c in CONSULTATIONS:
    rdv_entry = rdvs[c['rdv_idx']]
    rdv = rdv_entry['rdv']
    rdv_dt = rdv_entry['dt']
    try:
        consult, created = Consultation.objects.get_or_create(
            rendez_vous=rdv,
            defaults={
                'patient':        rdv.patient,
                'medecin':        rdv.medecin,
                'symptomes':      c['symptomes'],
                'examen_clinique': c['examen'],
                'diagnostic':     c['diagnostic'],
                'notes':          c['notes'],
                'ia_utilisee':    c['ia'],
                'suggestions_ia': c['ia_suggestions'],
            }
        )
        # Force la date_consultation à correspondre à la date du RDV
        # (auto_now_add ne peut pas être défini à la création)
        Consultation.objects.filter(pk=consult.pk).update(date_consultation=rdv_dt)
        consults_created.append(consult)
        consults_map[c['rdv_idx']] = consult
        print(f"  {'✓' if created else '→'} Consultation : {rdv.patient.prenom} {rdv.patient.nom} — {c['diagnostic'][:50]}…")
    except Exception as e:
        print(f"  ✗ Erreur consultation rdv_idx={c['rdv_idx']} : {e}", file=sys.stderr)

# ─────────────────────────────────────────────────────────────
# 5. Ordonnances
# ─────────────────────────────────────────────────────────────
PRESCRIPTIONS = [
    {
        'rdv_idx': 0,
        'notes': 'Traitement antihypertenseur renforcé. Régime hyposodé < 5g/j.',
        'lignes': [
            {'medicament': 'Amlodipine',  'dosage': '10mg', 'frequence': '1 comprimé le matin', 'duree': '30 jours'},
            {'medicament': 'Perindopril', 'dosage': '5mg',  'frequence': '1 comprimé le matin', 'duree': '30 jours'},
            {'medicament': 'Furosémide',  'dosage': '40mg', 'frequence': '1 comprimé le matin si œdèmes', 'duree': '15 jours'},
        ]
    },
    {
        'rdv_idx': 1,
        'notes': 'Objectif HbA1c < 7%. Autosurveillance glycémique 3x/j.',
        'lignes': [
            {'medicament': 'Metformine',                  'dosage': '1000mg', 'frequence': '1 comprimé midi et soir', 'duree': '90 jours'},
            {'medicament': 'Insuline Glargine (Lantus)',  'dosage': '10 UI',  'frequence': '1 injection sous-cutanée le soir', 'duree': '30 jours'},
            {'medicament': 'Atorvastatine',               'dosage': '40mg',   'frequence': '1 comprimé le soir', 'duree': '90 jours'},
        ]
    },
    {
        'rdv_idx': 5,
        'notes': 'Éviter allergènes (pollen, acariens). Aérer la maison le matin.',
        'lignes': [
            {'medicament': 'Budésonide/Formotérol (Symbicort)', 'dosage': '200/6 mcg',  'frequence': '2 inhalations matin et soir', 'duree': '30 jours'},
            {'medicament': 'Salbutamol (Ventoline)',             'dosage': '100 mcg',    'frequence': '2 bouffées si crise',          'duree': '30 jours'},
            {'medicament': 'Cétirizine',                         'dosage': '10mg',       'frequence': '1 comprimé le soir',           'duree': '30 jours'},
        ]
    },
    {
        'rdv_idx': 6,
        'notes': 'Arrêt tabac obligatoire. Vaccination grippe et pneumocoque recommandée.',
        'lignes': [
            {'medicament': 'Prednisolone',       'dosage': '40mg',   'frequence': '1 comprimé le matin pendant 5 jours', 'duree': '5 jours'},
            {'medicament': 'Tiotropium (Spiriva)','dosage': '18 mcg', 'frequence': '1 inhalation le matin',               'duree': '30 jours'},
            {'medicament': 'Amoxicilline',        'dosage': '1g',     'frequence': '1 comprimé 3x/j',                     'duree': '7 jours'},
        ]
    },
    {
        'rdv_idx': 7,
        'notes': 'Prise à jeun 30 min avant le repas du matin. Ne pas interrompre sans avis médical.',
        'lignes': [
            {'medicament': 'Lévothyroxine (Euthyrox)', 'dosage': '100 mcg', 'frequence': '1 comprimé le matin à jeun', 'duree': '90 jours'},
        ]
    },
    {
        'rdv_idx': 10,
        'notes': 'Repos relatif. Éviter port de charges > 5kg. Kinésithérapie 10 séances.',
        'lignes': [
            {'medicament': 'Ibuprofène',                        'dosage': '400mg', 'frequence': '1 comprimé 3x/j au repas', 'duree': '10 jours'},
            {'medicament': 'Thiocolchicoside (Myolastan)',       'dosage': '4mg',   'frequence': '1 comprimé matin et soir', 'duree': '7 jours'},
            {'medicament': 'Pantoprazole',                       'dosage': '20mg',  'frequence': '1 comprimé le matin à jeun', 'duree': '14 jours'},
        ]
    },
    {
        'rdv_idx': 12,
        'notes': 'Photoprotection stricte. Éviter exposition solaire. Suivi rhumatologue.',
        'lignes': [
            {'medicament': 'Hydroxychloroquine (Plaquenil)', 'dosage': '400mg', 'frequence': '1 comprimé le soir au repas', 'duree': '90 jours'},
            {'medicament': 'Prednisolone',                   'dosage': '20mg',  'frequence': '1 comprimé le matin', 'duree': '10 jours'},
        ]
    },
    {
        'rdv_idx': 18,
        'notes': 'Tenir un journal des crises. Éviter : stress, manque de sommeil, alcool.',
        'lignes': [
            {'medicament': 'Sumatriptan',  'dosage': '50mg', 'frequence': '1 comprimé dès début de crise (max 2/j)', 'duree': 'Au besoin'},
            {'medicament': 'Propranolol',  'dosage': '40mg', 'frequence': '1 comprimé matin et soir', 'duree': '90 jours'},
            {'medicament': 'Paracétamol',  'dosage': '1g',   'frequence': '1 comprimé si crise légère (max 4/j)', 'duree': 'Au besoin'},
        ]
    },
    {
        'rdv_idx': 23,
        'notes': 'Traitement antihypertenseur renforcé. Sel < 5g/j. Activité physique modérée.',
        'lignes': [
            {'medicament': 'Amlodipine',   'dosage': '10mg', 'frequence': '1 comprimé le matin', 'duree': '30 jours'},
            {'medicament': 'Ramipril',      'dosage': '10mg', 'frequence': '1 comprimé le soir',  'duree': '30 jours'},
            {'medicament': 'Atorvastatine', 'dosage': '40mg', 'frequence': '1 comprimé le soir',  'duree': '30 jours'},
        ]
    },
    {
        'rdv_idx': 24,
        'notes': 'Objectif HbA1c < 7.5%. Autosurveillance glycémique 4x/j.',
        'lignes': [
            {'medicament': 'Metformine',                 'dosage': '1000mg', 'frequence': '1 comprimé midi et soir', 'duree': '90 jours'},
            {'medicament': 'Insuline Glargine (Lantus)', 'dosage': '14 UI',  'frequence': '1 injection le soir',     'duree': '30 jours'},
        ]
    },
    {
        'rdv_idx': 31,
        'notes': 'Tenir un journal des crises. Éviter facteurs déclenchants.',
        'lignes': [
            {'medicament': 'Sumatriptan', 'dosage': '50mg', 'frequence': '1 comprimé dès début de crise', 'duree': 'Au besoin'},
            {'medicament': 'Propranolol', 'dosage': '40mg', 'frequence': '1 comprimé matin et soir',      'duree': '90 jours'},
        ]
    },
]

for p in PRESCRIPTIONS:
    rdv_idx = p['rdv_idx']
    if rdv_idx not in consults_map:
        print(f"  ⚠ Ordonnance ignorée (consultation rdv_idx={rdv_idx} non créée)")
        continue
    consult = consults_map[rdv_idx]
    try:
        presc, created = Prescription.objects.get_or_create(
            consultation=consult,
            defaults={
                'patient':        consult.patient,
                'medecin':        consult.medecin,
                'notes_generales': p['notes'],
            }
        )
        if created:
            for l in p['lignes']:
                LignePrescription.objects.get_or_create(
                    prescription=presc,
                    medicament=l['medicament'],
                    defaults={
                        'dosage':    l['dosage'],
                        'frequence': l['frequence'],
                        'duree':     l['duree'],
                    }
                )
            print(f"  ✓ Ordonnance : {consult.patient.prenom} {consult.patient.nom} ({len(p['lignes'])} médicament(s))")
        else:
            print(f"  → Ordonnance existante : {consult.patient.prenom} {consult.patient.nom}")
    except Exception as e:
        print(f"  ✗ Erreur ordonnance rdv_idx={rdv_idx} : {e}", file=sys.stderr)

# ─────────────────────────────────────────────────────────────
print("\n✅ Données de démonstration chargées avec succès !")
print(f"   👨‍⚕️ {len(medecins)} médecins  |  🏥 {len(patients)} patients")
print(f"   📅 {len(APPOINTMENTS)} rendez-vous  |  🩺 {len(CONSULTATIONS)} consultations")
print(f"   💊 {len(PRESCRIPTIONS)} ordonnances\n")
print("   Connexion médecin   : medecin / medecinpassword")
print("   Connexion démo      : dr.amrani / Demo2026!  (ou dr.hakimi, dr.bennis, dr.cherkaoui)")
print("   Connexion secrétaire: secretaire / secretairepassword")
print("   Connexion admin     : admin / adminpassword")
