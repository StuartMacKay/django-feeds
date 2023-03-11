from random import choice

from django.test import TestCase

import pytest
from django.urls import reverse

from feeds.models import Tag
from feeds.tests.factories import ArticleFactory, TagFactory
from feeds.tests.mixins import AdminTests


pytestmark = pytest.mark.django_db


class TagAdminTests(AdminTests, TestCase):
    factory_class = TagFactory
    query_count = 6


def test_merge_tags_action(admin_client):
    tags = TagFactory.create_batch(5)
    article = ArticleFactory(tags=tags)
    selected = choice(tags)

    url = reverse("admin:feeds_tag_changelist")
    data = {
        "post": "yes",
        "_selected_action": [tag.pk for tag in tags],
        "action": "merge_tags",
        "selected": selected.pk,
    }

    admin_client.post(url, data, follow=True)

    # Merged tags are deleted
    actual = [tag.pk for tag in Tag.objects.all()]
    assert actual == [selected.pk]

    # Merged tags are replaced
    actual = [tag.pk for tag in article.tags.all()]
    assert actual == [selected.pk]


def test_show_articles_for_tag_action(admin_client):
    tags = TagFactory.create_batch(5)
    selected = choice(tags)
    ArticleFactory.create_batch(10)

    url = reverse("admin:feeds_tag_changelist")
    data = {
        "post": "yes",
        "_selected_action": [selected.pk],
        "action": "show_articles",
    }

    response = admin_client.post(url, data, follow=True)

    request = response.request
    slugs = selected.slug

    assert request["PATH_INFO"] == reverse("admin:feeds_article_changelist")
    assert request["QUERY_STRING"] == f"tags__slug__in={slugs}"
