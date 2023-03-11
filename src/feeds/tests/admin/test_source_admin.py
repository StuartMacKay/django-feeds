from random import choice

from django.test import TestCase

import pytest
from django.urls import reverse

from feeds.tests.factories import ArticleFactory, SourceFactory
from feeds.tests.mixins import AdminTests

pytestmark = pytest.mark.django_db


class SourceAdminTests(AdminTests, TestCase):
    factory_class = SourceFactory
    query_count = 5


def test_show_articles_for_sources_action(admin_client):
    sources = SourceFactory.create_batch(5)
    selected = choice(sources)
    ArticleFactory.create_batch(10)

    url = reverse("admin:feeds_source_changelist")
    data = {
        "post": "yes",
        "_selected_action": [selected.pk],
        "action": "show_articles",
    }

    response = admin_client.post(url, data, follow=True)

    request = response.request
    slugs = selected.slug

    assert request["PATH_INFO"] == reverse("admin:feeds_article_changelist")
    assert request["QUERY_STRING"] == f"source__slug__in={slugs}"
