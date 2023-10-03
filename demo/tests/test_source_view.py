from django.urls import reverse
from django.utils import timezone

import pytest

from feeds.tests.conditions.articles import (
    only_published_articles,
    only_tags_for_articles,
)
from feeds.tests.conditions.querysets import is_ordered, is_paginated
from feeds.tests.conditions.responses import redirects_to, warning_message_shown
from feeds.tests.factories import (
    ArticleFactory,
    AuthorFactory,
    CategoryFactory,
    SourceFactory,
    TagFactory,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def source():
    return SourceFactory()


@pytest.fixture
def url(source):
    return reverse("source", args=(source.slug,))


@pytest.fixture
def articles(source):
    CategoryFactory.create(name="label/repost")
    CategoryFactory.create(name="label/updated")
    TagFactory.create_batch(20)
    AuthorFactory.create_batch(10)
    return ArticleFactory.create_batch(100, source=source)


def test_get(client, url, articles):
    response = client.get(url)
    articles = response.context["object_list"]
    tags = response.context["tags"]
    assert is_paginated(response)
    assert is_ordered(response)
    assert only_published_articles(articles, timezone.now())
    assert only_tags_for_articles(articles, tags)


def test_errors(client):
    response = client.get(reverse("source", args=("no-such-source",)), follow=True)
    assert response.status_code == 200
    assert redirects_to(response, reverse("sources"))
    assert warning_message_shown(response)


def test_query_count(client, url, articles, django_assert_num_queries):
    with django_assert_num_queries(6):
        client.get(url)
