import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atlasyx.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

users_to_check = ['admin', 'medecin', 'secretaire']
passwords = {
    'admin': 'adminpassword',
    'medecin': 'medecinpassword',
    'secretaire': 'secretairepassword'
}

print("=== CHECKING AND RESETTING PASSWORDS ===")
for username, data in passwords.items():
    try:
        user = User.objects.get(username=username)
        user.set_password(passwords[username])
        if username == 'admin':
            user.role = 'admin'
            user.is_superuser = True
            user.is_staff = True
        elif username == 'medecin':
            user.role = 'doctor'
            user.is_staff = False
            user.is_superuser = False
        elif username == 'secretaire':
            user.role = 'secretary'
            user.is_staff = False
            user.is_superuser = False
        user.save()
        print(f"User '{username}' password has been reset to '{passwords[username]}' and role ensured to '{user.role}'.")
    except User.DoesNotExist:
        print(f"User '{username}' DOES NOT EXIST. Please run 'python seed_users.py' (or similar script) to create them.")

print("Current users in system:")
for u in User.objects.all():
    print(f"- {u.username} (Role: {getattr(u, 'role', 'None')})")
