from django.utils import timezone

import pytest

from feeds.models import Article, Author
from feeds import loader
from feeds.tests.factories import FeedFactory

pytestmark = pytest.mark.django_db


@pytest.fixture()
def feed_template():
    return """<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom"
          xml:base="http://example.org/"
          xml:lang="en">
      <link rel="self" type="application/atom+xml"
            href="http://www.example.org/atom10.xml"/>
      <entry>
        <title>%(title)s</title>
        <link>%(url)s</link>
        <id>%(identifier)s</id>
        <updated>%(date)s</updated>
        <published>%(date)s</published>
        <author><name>%(author)s</name></author>
        <summary type="text">%(summary)s</summary>
        <category scheme="%(url)s" term="%(tags)s" />
      </entry>
    </feed>
    """


@pytest.fixture()
def feed_context():
    return {
        "title": "ARTICLE TITLE.",
        "url": "https://www.example.com/entry/",
        "date": timezone.now().strftime("%a, %d %b %Y %H:%M:%S %z"),
        "identifier": "Article:Identifier",
        "author": "Article Author",
        "summary": "Article Summary",
        "tags": "Tag",
    }


def test_blank_identifier(monkeypatch, feed_template, feed_context):
    """Feed entries with an empty identifier field are skipped"""

    def mock_return(feed):
        feed_context["identifier"] = ""
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.exists() is False


def test_missing_identifier(monkeypatch, feed_template, feed_context):
    """Feed entries with no identifier are loaded using the url as an identifier"""
    feed_template = feed_template.replace("<id>%(identifier)s</id>", "")

    def mock_return(feed):
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.exists() is True


def test_blank_title(monkeypatch, feed_template, feed_context):
    """Feed entries with an empty title field are skipped"""

    def mock_return(feed):
        feed_context["title"] = ""
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.exists() is False


def test_missing_title(monkeypatch, feed_template, feed_context):
    """Feed entries with no title field are skipped"""
    feed_template = feed_template.replace("<title>%(title)s</title>", "")

    def mock_return(feed):
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.exists() is False


def test_blank_link(monkeypatch, feed_template, feed_context):
    """Feed entries with an empty link field are skipped"""

    def mock_return(feed):
        feed_context["url"] = ""
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.exists() is False


def test_missing_link(monkeypatch, feed_template, feed_context):
    """Feed entries with no link field are skipped"""
    feed_template = feed_template.replace("<link>%(url)s</link>", "")

    def mock_return(feed):
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.exists() is False


def test_blank_date(monkeypatch, feed_template, feed_context):
    """Feed entries with an empty published field are skipped"""

    def mock_return(feed):
        feed_context["date"] = ""
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.exists() is False


def test_missing_date(monkeypatch, feed_template, feed_context):
    """Feed entries with no published field are skipped"""
    feed_template = feed_template.replace("<published>%(date)s</published>", "")

    def mock_return(feed):
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.exists() is False


def test_blank_author(monkeypatch, feed_template, feed_context):
    """Feed entries with an empty author field are loaded"""

    def mock_return(feed):
        feed_context["author"] = ""
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.get().authors.count() == 0


def test_missing_author(monkeypatch, feed_template, feed_context):
    """Feed entries with no author field are loaded"""
    feed_template = feed_template.replace(
        "<author><name>%(author)s</name></author>", ""
    )

    def mock_return(feed):
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.get().authors.count() == 0


def test_multiple_authors(monkeypatch, feed_template, feed_context):
    """Feeds where multiple Authors exist with the same name are loaded"""
    Author.objects.create(name=feed_context["author"])
    Author.objects.create(name=feed_context["author"])

    def mock_return(feed):
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.get().authors.count() == 1


def test_blank_summary(monkeypatch, feed_template, feed_context):
    """Feed entries with an empty summary field are loaded"""

    def mock_return(feed):
        feed_context["summary"] = ""
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.get().summary == ""


def test_missing_summary(monkeypatch, feed_template, feed_context):
    """Feed entries with no summary field are loaded"""
    feed_template = feed_template.replace(
        '<summary type="text">%(summary)s</summary>', ""
    )

    def mock_return(feed):
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    assert Article.objects.get().summary == ""


def test_blank_tags(monkeypatch, feed_template, feed_context):
    """Feed entries with an empty tag field are loaded"""

    def mock_return(feed):
        feed_context["tags"] = ""
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    article = Article.objects.get()
    actual = [tag.name for tag in article.tags.all()]
    assert actual == []


def test_missing_tags(monkeypatch, feed_template, feed_context):
    """Feed entries with no tag field are loaded"""
    feed_template = feed_template.replace(
        '<category scheme="%(url)s" term="%(tags)s" />', ""
    )

    def mock_return(feed):
        return feed_template % feed_context

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(FeedFactory.create(enabled=True))
    article = Article.objects.get()
    actual = [tag.name for tag in article.tags.all()]
    assert actual == []
