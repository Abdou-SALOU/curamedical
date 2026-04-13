from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.patients.models import Patient

User = get_user_model()

class PermissionsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Création des utilisateurs
        self.doctor = User.objects.create_user(username='dr_test', password='password', role='doctor')
        self.patient_user = User.objects.create_user(username='pt_test', password='password', role='patient')
        self.other_patient_user = User.objects.create_user(username='other_pt', password='password', role='patient')
        
        # Création des profils patients
        self.patient_profile = Patient.objects.create(
            user=self.patient_user,
            first_name='Patient',
            last_name='Test',
            national_id='PT123',
            date_of_birth='1990-01-01'
        )
        self.other_patient_profile = Patient.objects.create(
            user=self.other_patient_user,
            first_name='Other',
            last_name='Patient',
            national_id='PT456',
            date_of_birth='1992-02-02'
        )

    def test_patient_cannot_list_all_patients(self):
        """Vérifie qu'un patient ne peut pas voir la liste de tous les patients."""
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get('/api/patients/')
        # La liste doit être filtrée pour ne montrer que lui-même
        self.assertEqual(len(response.data.get('results', response.data)), 1)
        self.assertEqual(response.data.get('results', response.data)[0]['national_id'], 'PT123')

    def test_patient_cannot_access_other_patient_detail(self):
        """Vérifie qu'un patient ne peut pas accéder au dossier d'un autre."""
        self.client.force_authenticate(user=self.patient_user)
        response = self.client.get(f'/api/patients/{self.other_patient_profile.id}/')
        self.assertEqual(response.status_code, 403)

    def test_doctor_can_list_all_patients(self):
        """Vérifie qu'un médecin peut voir tous les patients."""
        self.client.force_authenticate(user=self.doctor)
        response = self.client.get('/api/patients/')
        self.assertEqual(len(response.data.get('results', response.data)), 2)

    def test_patient_cannot_create_patient(self):
        """Vérifie qu'un patient ne peut pas créer de nouveau patient."""
        self.client.force_authenticate(user=self.patient_user)
        data = {
            'first_name': 'Hacker',
            'last_name': 'Test',
            'national_id': 'BAD007',
            'date_of_birth': '2000-01-01'
        }
        response = self.client.post('/api/patients/', data)
        self.assertEqual(response.status_code, 403)
