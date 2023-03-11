import os

from celery.schedules import crontab  # type: ignore

from .app import app

FEED_TASK_SCHEDULE = os.environ.get("FEED_TASK_SCHEDULE", "0 * * * *")
minute, hour, day_of_week, day_of_month, month_of_year = FEED_TASK_SCHEDULE.split()

app.conf.beat_schedule = {
    "load-feeds": {
        "task": "feeds.tasks.load_feeds",
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
