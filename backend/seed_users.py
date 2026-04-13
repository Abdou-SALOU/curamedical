import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

admin_pwd = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')
doctor_pwd = os.getenv('DJANGO_DOCTOR_PASSWORD', 'medecinpassword')
sec_pwd = os.getenv('DJANGO_SECRETARY_PASSWORD', 'secretairepassword')

users_data = [
    {'username': 'admin', 'password': admin_pwd, 'role': 'admin', 'is_superuser': True, 'is_staff': True, 'first_name': 'Super', 'last_name': 'Admin'},
    {'username': 'medecin', 'password': doctor_pwd, 'role': 'doctor', 'is_superuser': False, 'is_staff': False, 'first_name': 'Jean', 'last_name': 'Dupont'},
    {'username': 'secretaire', 'password': sec_pwd, 'role': 'secretary', 'is_superuser': False, 'is_staff': False, 'first_name': 'Alice', 'last_name': 'Martin'},
]

for data in users_data:
    if not User.objects.filter(username=data['username']).exists():
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            role=data['role'],
            is_superuser=data['is_superuser'],
            is_staff=data['is_staff'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        print(f"Created user: {data['username']}")
    else:
        print(f"User {data['username']} already exists")
