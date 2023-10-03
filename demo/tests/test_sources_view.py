from django.urls import reverse

import pytest

from feeds.tests.conditions.querysets import is_ordered, is_paginated
from feeds.tests.factories import SourceFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    return reverse("sources")


@pytest.fixture
def sources():
    return SourceFactory.create_batch(50)


def test_get(client, url, sources):
    response = client.get(url)
    assert is_paginated(response)
    assert is_ordered(response)


def test_query_count(client, url, sources, django_assert_num_queries):
    # Includes a query to fetch the current site though this
    # query does not appear in the debug toolbar
    with django_assert_num_queries(2):
        client.get(url)
