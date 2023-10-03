import pytest
from django.urls import reverse

from feeds.tests.conditions.articles import article_was_clicked
from feeds.tests.conditions.responses import redirects_to
from feeds.tests.factories import ArticleFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def article():
    return ArticleFactory()


def test_view(client, article):
    response = client.get(
        reverse("article", kwargs={"code": article.code}), follow=False
    )
    assert redirects_to(response, article.url)
    assert article_was_clicked(article)


def test_click_view(client, article):
    response = client.post(reverse("article-click"), data={"code": article.code})
    assert response.status_code == 204
    assert article_was_clicked(article)
