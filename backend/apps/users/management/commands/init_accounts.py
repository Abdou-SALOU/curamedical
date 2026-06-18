from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize default accounts for Admin, Doctor and Secretary'

    def handle(self, *args, **options):
        # Data to seed
        users_data = [
            {
                'username': 'admin',
                'password': 'adminpassword',
                'role': 'administrateur',
                'email': 'admin@CuraMedical.com',
                'first_name': 'Super',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'username': 'medecin',
                'password': 'medecinpassword',
                'role': 'medecin',
                'email': 'medecin@CuraMedical.com',
                'first_name': 'Nouridine',
                'last_name': 'Sawadogo',
                'is_staff': True,
                'specialite': 'Médecine Générale'
            },
            {
                'username': 'secretaire',
                'password': 'secretairepassword',
                'role': 'secretaire',
                'email': 'secretaire@CuraMedical.com',
                'first_name': 'Secrétaire',
                'last_name': 'CuraMedical',
                'is_staff': True
            }
        ]

        for udata in users_data:
            username = udata['username']
            password = udata.pop('password')
            
            user, created = User.objects.get_or_create(username=username, defaults=udata)
            
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully created user: {username}'))
            else:
                # Update existing user role and flags
                for key, value in udata.items():
                    setattr(user, key, value)
                user.save()
                self.stdout.write(self.style.WARNING(f'User {username} already exists, updated its roles/flags'))

        self.stdout.write(self.style.SUCCESS('Initialization complete.'))
