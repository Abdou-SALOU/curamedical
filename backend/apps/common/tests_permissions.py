from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.patients.models import Patient

User = get_user_model()


class PermissionsPatientsTestCase(TestCase):
    """Contrôle d'accès (RBAC) sur l'API patients.

    Reflète le comportement réel du `PatientViewSet` :
      - patient    → ne voit que SON propre dossier ;
      - secrétaire → voit tous les patients, peut en créer ;
      - médecin    → ne voit que les patients qui lui sont liés (RDV/consultation),
                     peut en créer ;
      - administrateur → aucun accès aux données médicales ;
      - création réservée aux rôles médecin/secrétaire.
    """

    def setUp(self):
        self.client = APIClient()

        # ── Utilisateurs (rôles réels du modèle) ──────────────────
        self.admin = User.objects.create_user(
            username='admin_test', password='pass', role='administrateur')
        self.medecin = User.objects.create_user(
            username='dr_test', password='pass', role='medecin')
        self.secretaire = User.objects.create_user(
            username='sec_test', password='pass', role='secretaire')
        self.patient_user = User.objects.create_user(
            username='pt_test', password='pass', role='patient')
        self.autre_patient_user = User.objects.create_user(
            username='pt_autre', password='pass', role='patient')

        # ── Dossiers patients (champs réels, en français) ─────────
        self.patient_profile = Patient.objects.create(
            utilisateur=self.patient_user,
            nom='Patient', prenom='Test',
            date_naissance='1990-01-01', sexe='M',
            telephone='0600000001', cin='PT123',
        )
        self.autre_profile = Patient.objects.create(
            utilisateur=self.autre_patient_user,
            nom='Autre', prenom='Patient',
            date_naissance='1992-02-02', sexe='F',
            telephone='0600000002', cin='PT456',
        )

    @staticmethod
    def _items(response):
        """Extrait la liste, que la réponse soit paginée ou non."""
        data = response.data
        return data.get('results', data) if isinstance(data, dict) else data

    # ── Accès anonyme ─────────────────────────────────────────────
    def test_anonyme_refuse(self):
        """Sans authentification, l'API patients renvoie 401."""
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, 401)

    # ── Rôle patient ──────────────────────────────────────────────
    def test_patient_voit_seulement_son_dossier(self):
        """Un patient ne voit que son propre dossier dans la liste."""
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, 200)
        items = self._items(response)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['cin'], 'PT123')

    def test_patient_ne_voit_pas_autre_dossier(self):
        """Le dossier d'un autre patient est hors périmètre → 404."""
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get(f'/api/patients/{self.autre_profile.id}/')
        self.assertEqual(response.status_code, 404)

    def test_patient_ne_peut_pas_creer(self):
        """Un patient ne peut pas créer de dossier → 403."""
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.post('/api/patients/', {
            'nom': 'Pirate', 'prenom': 'Test',
            'date_naissance': '2000-01-01', 'sexe': 'M',
            'telephone': '0600000003', 'cin': 'HACK1',
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Patient.objects.filter(cin='HACK1').exists())

    # ── Rôle secrétaire ───────────────────────────────────────────
    def test_secretaire_voit_tous_les_patients(self):
        """La secrétaire voit l'ensemble des patients validés."""
        self.client.force_authenticate(user=self.secretaire)
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self._items(response)), 2)

    def test_secretaire_peut_creer(self):
        """La secrétaire peut créer un dossier patient → 201."""
        self.client.force_authenticate(user=self.secretaire)
        response = self.client.post('/api/patients/', {
            'nom': 'Nouveau', 'prenom': 'Patient',
            'date_naissance': '1985-05-05', 'sexe': 'F',
            'telephone': '0600000004', 'cin': 'NEW001',
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Patient.objects.filter(cin='NEW001').exists())

    # ── Rôle médecin ──────────────────────────────────────────────
    def test_medecin_peut_creer(self):
        """Le médecin peut créer un dossier patient → 201."""
        self.client.force_authenticate(user=self.medecin)
        response = self.client.post('/api/patients/', {
            'nom': 'Patient', 'prenom': 'DuMedecin',
            'date_naissance': '1978-03-03', 'sexe': 'M',
            'telephone': '0600000005', 'cin': 'MED001',
        })
        self.assertEqual(response.status_code, 201)

    # ── Rôle administrateur ───────────────────────────────────────
    def test_admin_n_a_pas_acces_aux_donnees_medicales(self):
        """L'administrateur ne voit aucun patient (cloisonnement)."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self._items(response)), 0)
