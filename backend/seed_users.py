import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curamedical.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

admin_pwd = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')
doctor_pwd = os.getenv('DJANGO_DOCTOR_PASSWORD', 'medecinpassword')
sec_pwd = os.getenv('DJANGO_SECRETARY_PASSWORD', 'secretairepassword')

users_data = [
    {'username': 'admin', 'password': admin_pwd, 'role': 'administrateur', 'is_superuser': True, 'is_staff': True, 'first_name': 'Super', 'last_name': 'Admin'},
    {'username': 'medecin', 'password': doctor_pwd, 'role': 'medecin', 'is_superuser': False, 'is_staff': True, 'first_name': 'Nouridine', 'last_name': 'Sawadogo', 'specialite': 'Médecine Générale'},
    {'username': 'secretaire', 'password': sec_pwd, 'role': 'secretaire', 'is_superuser': False, 'is_staff': True, 'first_name': 'Secretariat', 'last_name': 'Predict'},
]

for data in users_data:
    user, created = User.objects.get_or_create(username=data['username'])
    if created:
        user.set_password(data['password'])
        print(f"Created user: {data['username']}")
    else:
        print(f"User {data['username']} already exists - Updating role and status...")
    
    user.role = data['role']
    user.is_superuser = data['is_superuser']
    user.is_staff = data['is_staff']
    user.first_name = data['first_name']
    user.last_name = data['last_name']
    if data.get('specialite'):
        user.specialite = data['specialite']
    user.save()

print("Initial users seeded successfully.")
