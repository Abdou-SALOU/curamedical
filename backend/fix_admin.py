import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medpredict.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'change-me-immediately')

u, created = User.objects.get_or_create(username='admin', defaults={
    'role': 'admin',
    'is_superuser': True,
    'is_staff': True,
    'first_name': 'Super',
    'last_name': 'Admin'
})
u.set_password(password)
u.is_active = True
u.save()

if created:
    print(f"Created user: admin")
else:
    print("Updated password for user: admin from environment variable")
