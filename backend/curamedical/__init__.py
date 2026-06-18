# Charge l'application Celery au démarrage de Django pour que les
# décorateurs @shared_task soient liés au bon broker.
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery non installé (ex: environnement local sans worker) —
    # les notifications basculeront sur des threads via dispatch_task().
    celery_app = None
