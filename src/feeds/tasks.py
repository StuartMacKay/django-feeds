from feeds.services import feeds, opengraph

from feeds.models import Article
from demo.conf.celery.app import app


@app.task()
def load_feeds() -> None:
    feeds.load_feeds()


@app.task
def load_opengraph_tags(pk: str) -> None:
    opengraph.load_tags(Article.objects.get(pk=pk))
