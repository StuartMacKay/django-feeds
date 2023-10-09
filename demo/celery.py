import os

from celery import Celery  # type: ignore
from celery.schedules import crontab
from celery.signals import setup_logging  # type: ignore

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo.settings")

app = Celery()


class CeleryConfig:
    # Configure logging using Django's LOGGING setting. Caveat: since logging
    # is configured using the setup_logging signal, see below, this might not
    # be needed.
    worker_hijack_root_logger = False

    # The default, unless it is overridden using an environment variable
    # is to assume we are running the demo using a virtualenv and connect
    # to a locally install instance of rabbitmq. When using containers,
    # the broker url will be set to connect to the rabbitmq service.
    broker_url = os.environ.get(
        "CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672/"
    )


# Load the configuration
app.config_from_object(CeleryConfig)
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# A celery task runs every hour, on the error and checked the schedule for
# each active feed. If the schedule, also a crontab, matches the current
# time then the feed is loaded. This two-level approach comes in useful for
# feeds that are either updated in frequently, so there's no need to cook
# the planet by checking every hour, or, dealing with throttling by services
# such as Cloudflare, where too many request s

FEEDS_TASK_SCHEDULE = os.environ.get("FEEDS_TASK_SCHEDULE", "0 * * * *")
minute, hour, day_of_week, day_of_month, month_of_year = FEEDS_TASK_SCHEDULE.split()

app.conf.beat_schedule = {
    "load-feeds": {
        "task": "demo.tasks.load_feeds",
        "schedule": crontab(
            minute=minute,
            hour=hour,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year,
        ),
    },
    "daily-digest": {
        "task": "feed.tasks.daily_digest",
        "schedule": crontab(minute="0", hour="2"),  # 2am, each day
    },
}

# Since the feeds are loaded regularly there is no need to write messages
# to disk so they can simply be thrown away if the broker or workers are
# not available. Caveat: Not entirely sure this is working as expected.
# Some queuing of messages does appear to be happending.

app.conf.task_routes = {
    "demo.tasks.load_feeds": {"delivery_mode": "transient"},
}


@setup_logging.connect
def receiver_setup_logging(loglevel, logfile, format, colorize, **kwargs):  # noqa
    from logging.config import dictConfig
    from django.conf import settings

    dictConfig(settings.LOGGING)
