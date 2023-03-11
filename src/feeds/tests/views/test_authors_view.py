from django.urls import reverse

import pytest

from feeds.tests.conditions.querysets import is_ordered, is_paginated
from feeds.tests.factories import ArticleFactory, AuthorFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    return reverse("feeds:authors")


@pytest.fixture
def authors():
    authors = AuthorFactory.create_batch(50)
    ArticleFactory.create_batch(100)
    return authors


def test_get(client, url, authors):
    response = client.get(url)
    assert is_paginated(response)
    assert is_ordered(response)


def test_query_count(client, url, authors, django_assert_num_queries):
    with django_assert_num_queries(2):
        client.get(url)
