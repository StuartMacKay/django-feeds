from django.db.models import F

from feeds.models import Article

__all__ = (
    "article_clicked",
)


def article_clicked(article: Article) -> None:
    article.views = F("views") + 1
    article.save()
