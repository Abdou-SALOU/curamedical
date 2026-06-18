"""
Comptes de démonstration aux noms de l'équipe (3 membres) + admin par défaut.

  • Médecin     : Dr Nouredine SAWADOGO   (orthographe alignée sur le cachet signature.png)
  • Secrétaire  : Kamara MACIRE
  • Patient     : Abdou SALOU             (relié à un dossier clinique riche)
  • Admin       : admin (inchangé)

Toutes les données cliniques (RDV, consultations, ordonnances) sont consolidées sous
le Dr SAWADOGO afin que le NOM imprimé sur chaque ordonnance / compte rendu corresponde
au cachet (apps/common/signature.png : « Dr Nouredine Sawadogo »).

Lancer : docker-compose exec backend python seed_team_accounts.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curamedical.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.patients.models import Patient
from apps.appointments.models import RendezVous
from apps.consultations.models import Consultation
from apps.prescriptions.models import Prescription

User = get_user_model()

# ── 1. Médecin : Dr Nouredine SAWADOGO ────────────────────────────────
med, _ = User.objects.get_or_create(username='medecin')
med.set_password('medecinpassword')
med.first_name = 'Nouredine'
med.last_name = 'SAWADOGO'
med.email = 'n.sawadogo@curamedical.io'
med.role = 'medecin'
med.is_staff = True
for field, value in (('specialite', 'Médecine Générale'), ('telephone', '+212522001122')):
    if hasattr(med, field):
        setattr(med, field, value)
med.save()

# Consolide TOUTES les données cliniques sous le Dr SAWADOGO → cachet cohérent partout
n_rdv = RendezVous.objects.all().update(medecin=med)
n_cons = Consultation.objects.all().update(medecin=med)
n_presc = Prescription.objects.all().update(medecin=med)

# ── 2. Secrétaire : Kamara MACIRE ─────────────────────────────────────
sec, _ = User.objects.get_or_create(username='secretaire')
sec.set_password('secretairepassword')
sec.first_name = 'Kamara'
sec.last_name = 'MACIRE'
sec.email = 'k.macire@curamedical.io'
sec.role = 'secretaire'
sec.is_staff = True
sec.save()

# ── 3. Patient : Abdou SALOU (relié à un dossier riche) ───────────────
dossier = Patient.objects.filter(cin='BE123456').first() or Patient.objects.first()
dossier.prenom = 'Abdou'
dossier.nom = 'SALOU'
dossier.email = 'abdousalou08@gmail.com'

pat, _ = User.objects.get_or_create(username='abdou.salou')
pat.set_password('Demo2026!')
pat.first_name = 'Abdou'
pat.last_name = 'SALOU'
pat.email = 'abdousalou08@gmail.com'
pat.role = 'patient'
pat.is_staff = False
pat.save()

dossier.utilisateur = pat
dossier.save()

# Nettoie un éventuel ancien compte patient de démo
User.objects.filter(username='patient.demo').exclude(pk=pat.pk).delete()

print("✅ Comptes équipe configurés :")
print(f"   👨‍⚕️ Médecin    : medecin / medecinpassword        → Dr Nouredine SAWADOGO")
print(f"   🗂️  Secrétaire : secretaire / secretairepassword   → Kamara MACIRE")
print(f"   🧑  Patient    : abdou.salou / Demo2026!           → Abdou SALOU (dossier {dossier.cin})")
print(f"   🛡️  Admin      : admin / adminpassword              (inchangé)")
print(f"   📊 Données consolidées sous SAWADOGO : {n_rdv} RDV, {n_cons} consultations, {n_presc} ordonnances")
