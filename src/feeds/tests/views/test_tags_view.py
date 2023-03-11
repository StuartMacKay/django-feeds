from django.urls import reverse

import pytest

from feeds.tests.conditions.querysets import is_ordered, is_paginated
from feeds.tests.factories import TagFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    return reverse("feeds:tags")


@pytest.fixture
def tags():
    return TagFactory.create_batch(100)


def test_get(client, url, tags):
    response = client.get(url)
    assert is_paginated(response)
    assert is_ordered(response)


def test_query_count(client, url, tags, django_assert_num_queries):
    # Includes a query to fetch the current site though this
    # query does not appear in the debug toolbar
    with django_assert_num_queries(2):
        client.get(url)
