import config
from celery import Celery


# Initialize Celery
celery = Celery(
    "worker",
    broker=config.CeleryConfig.CELERY_BROKER_URL,
    backend=config.CeleryConfig.CELERY_RESULT_BACKEND,
)


@celery.task()
def func1(arg):
    ...
    return ...
