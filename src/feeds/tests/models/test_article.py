import datetime as dt

from django.utils import timezone

import pytest

from feeds.models import Article
from feeds.tests.factories import ArticleFactory

pytestmark = pytest.mark.django_db


def test_published():
    today = timezone.now()
    ArticleFactory.create(title="first", date=today, publish=True)
    ArticleFactory.create(title="second", date=today, publish=False)
    queryset = Article.objects.published()
    assert queryset.count() == 1
    assert queryset.first().title == "first"


def test_for_date():
    today = timezone.now()
    ArticleFactory.create(title="first", date=today - dt.timedelta(days=1))
    ArticleFactory.create(title="second", date=today)
    ArticleFactory.create(title="first", date=today + dt.timedelta(days=1))
    queryset = Article.objects.for_date(today)
    assert queryset.count() == 1
    assert queryset.first().title == "second"
