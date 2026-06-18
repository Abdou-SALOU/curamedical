from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,backend').split(',')

# Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Packages tiers
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',

    # Nos applications
    'apps.users',
    'apps.patients',
    'apps.appointments',
    'apps.consultations',
    'apps.prescriptions',
    'apps.chat',
    'apps.whatsapp',
    'auditlog',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
]

ROOT_URLCONF = 'curamedical.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'Templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Base de données PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD': config('POSTGRES_PASSWORD'),
        'HOST': config('POSTGRES_HOST', default='db'),
        'PORT': '5432',
    }
}

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'users.User'

# Configuration JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'curamedical.pagination.CustomPagination',
    # Rate limiting — protège contre le brute-force sur /api/auth/login/
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/minute',
        'user': '300/minute',
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Documentation API (Swagger / OpenAPI)
SPECTACULAR_SETTINGS = {
    'TITLE': 'CuraMedical API',
    'DESCRIPTION': 'API REST du système de gestion médicale CuraMedical',
    'VERSION': '2.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# CORS (autorise le frontend React)
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://localhost:5173'
).split(',')
CORS_ALLOW_CREDENTIALS = True

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Casablanca'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Celery (file de tâches asynchrones) ────────────────────────
# Broker = Redis. Les notifications (email, WhatsApp, PDF, n8n) sont
# déléguées à un worker Celery pour ne jamais bloquer la requête HTTP.
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 120          # tue une tâche bloquée après 2 min
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
# Si False (défaut local sans worker) : exécution synchrone in-process
# via un thread — voir apps.common.tasks.dispatch_task.
CELERY_TASK_ALWAYS_EAGER = config('CELERY_TASK_ALWAYS_EAGER', default=False, cast=bool)

# ── Microservice IA ────────────────────────────────────────────
IA_SERVICE_URL = config('IA_SERVICE_URL', default='http://ia-service:5000')
GROQ_API_KEY   = config('GROQ_API_KEY', default='')

# ── Twilio / WhatsApp ──────────────────────────────────────────
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN  = config('TWILIO_AUTH_TOKEN',  default='')
# Numéro Twilio WhatsApp sandbox (ex: +14155238886) ou numéro approuvé
TWILIO_WHATSAPP_FROM = config('TWILIO_WHATSAPP_FROM', default='+14155238886')
# En prod : URL publique du backend (ex: https://api.curamedical.com)
# En dev avec ngrok : https://xxxx.ngrok.io
PUBLIC_BASE_URL = config('PUBLIC_BASE_URL', default='')
# Activer la vérification de signature Twilio (mettre True en production)
TWILIO_VALIDATE_SIGNATURE = config('TWILIO_VALIDATE_SIGNATURE', default=False, cast=bool)

# ── Webhook n8n ────────────────────────────────────────────────
N8N_WEBHOOK_URL = config('N8N_WEBHOOK_URL', default='http://localhost:5678/webhook/prescriptions')

# ── Email SMTP ─────────────────────────────────────────────────
# En dev : backend=console → emails affichés dans le terminal Django
# En prod : backend=smtp  → emails envoyés via Gmail / autre SMTP
EMAIL_BACKEND  = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST     = config('EMAIL_HOST',    default='smtp.gmail.com')
EMAIL_PORT     = config('EMAIL_PORT',    default=587, cast=int)
EMAIL_USE_TLS  = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER     = config('EMAIL_HOST_USER',     default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL  = config('DEFAULT_FROM_EMAIL',  default='CuraMedical <noreply@curamedical.com>')

# ── Logging ────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}
