from django.urls import reverse
from django.utils import timezone

import pytest

from feeds.tests.conditions.articles import only_published_articles, only_tags_for_articles
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
def author():
    return AuthorFactory()


@pytest.fixture
def url(author):
    return reverse("feeds:author", args=(author.slug,))


@pytest.fixture
def articles(author):
    CategoryFactory.create(name="label/repost")
    CategoryFactory.create(name="label/updated")
    TagFactory.create_batch(20)
    SourceFactory.create_batch(20)
    return ArticleFactory.create_batch(100, authors=[author])


def test_get(client, url, author, articles):
    response = client.get(url)
    articles = response.context["object_list"]
    tags = response.context["tags"]
    assert is_paginated(response)
    assert is_ordered(response)
    assert only_published_articles(articles, timezone.now())
    assert only_tags_for_articles(articles, tags)


def test_errors(client):
    response = client.get(reverse("feeds:author", args=("no-such-author",)), follow=True)
    assert response.status_code == 200
    assert redirects_to(response, reverse("feeds:authors"))
    assert warning_message_shown(response)


def test_query_count(client, url, articles, django_assert_num_queries):
    with django_assert_num_queries(4):
        client.get(url)
