from feeds.models import Article


def only_published_articles(articles, timestamp) -> bool:
    return all(article.date and article.date < timestamp for article in articles)


def article_was_clicked(obj: Article) -> bool:
    views = obj.views
    obj.refresh_from_db()
    return views + 1 == obj.views


def only_tags_for_articles(articles, tags) -> bool:
    expected = set([tag.pk for article in articles for tag in article.tags.all()])
    actual = [tag.pk for tag in tags]
    return sorted(actual) == sorted(expected)


def only_articles_between_dates(articles, start_date, end_date) -> bool:
    return all(start_date <= article.date.date() <= end_date for article in articles)
