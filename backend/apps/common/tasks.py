"""Aiguillage des tâches asynchrones.

`dispatch_task` envoie une tâche Celery au worker via Redis. Si le broker
est injoignable (Redis arrêté, worker absent — fréquent en dev/démo), on
bascule automatiquement sur un thread daemon pour ne jamais perdre la
notification ni bloquer la requête HTTP.
"""
import logging
import threading

logger = logging.getLogger(__name__)


def dispatch_task(task, *args, **kwargs):
    """Exécute une tâche Celery, avec repli sur thread si le broker est KO.

    `task` est un objet décoré par @shared_task. On tente `.delay(...)`;
    en cas d'échec (connexion Redis, etc.) on relance la fonction sous-jacente
    dans un thread daemon.
    """
    try:
        return task.delay(*args, **kwargs)
    except Exception as exc:  # OperationalError, ConnectionError, etc.
        logger.warning(
            "[tasks] Broker Celery indisponible (%s) — repli sur thread pour %s",
            exc, getattr(task, 'name', task),
        )
        thread = threading.Thread(
            target=_run_task_safely,
            args=(task, args, kwargs),
            daemon=True,
        )
        thread.start()
        return None


def _run_task_safely(task, args, kwargs):
    try:
        # .run() exécute le corps de la tâche en synchrone, sans broker
        task.run(*args, **kwargs)
    except Exception as exc:
        logger.error("[tasks] Échec exécution thread de %s : %s",
                     getattr(task, 'name', task), exc)
