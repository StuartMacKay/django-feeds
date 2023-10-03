from django.urls import reverse
from django.utils import timezone

import pytest

from feeds.models import Author, Source
from feeds.tests.conditions.articles import only_published_articles
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
def tag():
    return TagFactory()


@pytest.fixture
def url(tag):
    return reverse("tag", args=(tag.slug,))


@pytest.fixture
def articles(tag):
    CategoryFactory.create(name="label/repost")
    CategoryFactory.create(name="label/updated")
    SourceFactory.create_batch(20)
    AuthorFactory.create_batch(10)
    return ArticleFactory.create_batch(100, tags=[tag])


def test_get(client, url, articles):
    response = client.get(url)
    articles = response.context["object_list"]
    assert is_paginated(response)
    assert is_ordered(response)
    assert only_published_articles(articles, timezone.now())


def test_errors(client):
    response = client.get(reverse("tag", args=("no-such-tag",)), follow=True)
    assert response.status_code == 200
    assert redirects_to(response, reverse("tags"))
    assert warning_message_shown(response)


def test_tag_for_author(client, tag, articles):
    author = Author.objects.first()
    url = reverse("tag-author", args=(tag.slug, author.slug))
    response = client.get(url)
    expected = [obj.pk for obj in author.articles.published()]
    actual = [obj.pk for obj in response.context["object_list"]]
    assert sorted(actual) == sorted(expected)


def test_tag_for_source(client, tag, articles):
    source = Source.objects.first()
    url = reverse("tag-source", args=(tag.slug, source.slug))
    response = client.get(url)
    expected = [obj.pk for obj in source.articles.published()]
    actual = [obj.pk for obj in response.context["object_list"]]
    assert sorted(actual) == sorted(expected)


def test_query_count(client, url, articles, django_assert_num_queries):
    with django_assert_num_queries(5):
        client.get(url)
