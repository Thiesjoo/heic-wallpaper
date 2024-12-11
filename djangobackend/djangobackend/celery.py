import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangobackend.settings')

app = Celery('djangobackend')

# celery.conf.beat_schedule = {
#     'remove_old_images': {
#         'task': 'backend.worker.image_processor.remove_broken_images',
#         'schedule': DatabaseConfig.CLEANUP_INTERVAL,
#     }
# }


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
