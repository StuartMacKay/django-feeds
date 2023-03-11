import os

broker_url = os.environ.get("BROKER_URL", "")

task_always_eager = broker_url == ""

accept_content = ["json"]

worker_hijack_root_logger = False

task_routes = {
    "feeds.tasks.load_feeds": {"delivery_mode": "transient"},
}

beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
