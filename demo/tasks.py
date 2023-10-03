from feeds import loader

from .celery import app


@app.task()
def load_feeds() -> None:
    loader.load_feeds()
