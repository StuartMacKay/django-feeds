import datetime as dt

from django.urls import reverse
from django.utils import timezone

import pytest

from feeds.tests.conditions.articles import (
    only_articles_between_dates,
    only_published_articles,
    only_tags_for_articles,
)
from feeds.tests.conditions.querysets import is_ordered, is_paginated
from feeds.tests.factories import (
    ArticleFactory,
    AuthorFactory,
    CategoryFactory,
    TagFactory,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    return reverse("articles")


@pytest.fixture
def articles():
    CategoryFactory.create(name="label/repost")
    CategoryFactory.create(name="label/updated")
    TagFactory.create_batch(20)
    AuthorFactory.create_batch(10)
    return ArticleFactory.create_batch(100)


def test_get(client, url, articles):
    response = client.get(url)
    articles = response.context["object_list"]
    tags = response.context["tags"]
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=6)
    assert is_paginated(response)
    assert is_ordered(response)
    assert only_published_articles(articles, timezone.now())
    assert only_tags_for_articles(articles, tags)
    assert only_articles_between_dates(articles, start_date, end_date)


def test_query_count(client, url, articles, django_assert_num_queries):
    with django_assert_num_queries(8):
        client.get(url)
