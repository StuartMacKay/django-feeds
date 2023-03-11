from unittest import mock

from django.test import TestCase

import pytest
from django.urls import reverse

from feeds.tests.factories import FeedFactory
from feeds.tests.mixins import AdminTests


pytestmark = pytest.mark.django_db


class FeedAdminTests(AdminTests, TestCase):
    factory_class = FeedFactory
    query_count = 6


def mock_load_feed(feed):
    pass


@mock.patch("feeds.services.feeds.load_feed")
def test_feed_load_feed_action(mocked, admin_client):
    mocked.side_effect = mock_load_feed
    feed = FeedFactory.create()
    url = reverse("admin:feeds_feed_changelist")
    data = {"action": "load_feed", "_selected_action": [str(feed.pk)]}

    response = admin_client.post(url, data, follow=True)

    assert response.status_code == 200
    assert mocked.call_count == 1
