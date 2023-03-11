from celery import Celery  # type: ignore
from django_structlog.celery.steps import DjangoStructLogInitStep  # type: ignore

app = Celery()

# Load the configuration
app.config_from_object("demo.conf.celery.config")
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
# Configure workers to use structlog
app.steps["worker"].add(DjangoStructLogInitStep)
