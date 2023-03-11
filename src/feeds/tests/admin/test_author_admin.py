from random import choice

from django.test import TestCase

import pytest
from django.urls import reverse

from feeds.models import Author
from feeds.tests.factories import ArticleFactory, AuthorFactory
from feeds.tests.mixins import AdminTests

pytestmark = pytest.mark.django_db


class AuthorAdminTests(AdminTests, TestCase):
    factory_class = AuthorFactory
    query_count = 6


def test_merge_authors_action(admin_client):
    authors = AuthorFactory.create_batch(5)
    article = ArticleFactory(authors=authors)
    selected = choice(authors)

    url = reverse("admin:feeds_author_changelist")
    data = {
        "post": "yes",
        "_selected_action": [author.pk for author in authors],
        "action": "merge_authors",
        "selected": selected.pk,
    }

    admin_client.post(url, data, follow=True)

    # Merged authors are deleted
    actual = [author.pk for author in Author.objects.all()]
    assert actual == [selected.pk]

    # Merged author are replaced
    actual = [author.pk for author in article.authors.all()]
    assert actual == [selected.pk]


def test_show_articles_for_authors_action(admin_client):
    authors = AuthorFactory.create_batch(5)
    selected = choice(authors)
    ArticleFactory.create_batch(10)

    url = reverse("admin:feeds_author_changelist")
    data = {
        "post": "yes",
        "_selected_action": [selected.pk],
        "action": "show_articles",
    }

    response = admin_client.post(url, data, follow=True)

    request = response.request
    slugs = selected.slug

    assert request["PATH_INFO"] == reverse("admin:feeds_article_changelist")
    assert request["QUERY_STRING"] == f"authors__slug__in={slugs}"
