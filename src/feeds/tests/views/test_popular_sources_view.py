from django.urls import reverse

import pytest

from feeds.tests.conditions.querysets import is_ordered, is_paginated
from feeds.tests.factories import SourceFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def url():
    return reverse("feeds:sources-popular")


@pytest.fixture
def sources():
    return SourceFactory.create_batch(40)


def test_get(client, url, sources):
    response = client.get(url)
    assert is_paginated(response)
    assert is_ordered(response)
