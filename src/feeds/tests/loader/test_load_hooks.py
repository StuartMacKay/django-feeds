from django.template import Context, Template
from django.utils import timezone

import pytest

from feeds.models import Article
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
        <title>{{ title }}</title>
        <link>{{ url }}</link>
        <id>{{ identifier }}</id>
        <updated>{{ date_str }}</updated>
        <published>{{ date_str }}</published>
        <author><name>{{ author }}</name></author>
        <summary type="text">{{ summary }}</summary>
        {% for tag in tags %}
          <category scheme="{{ url }}" term="{{ tag }}" />
        {% endfor %}
      </entry>
    </feed>
    """


@pytest.fixture()
def feed_context():
    # The context contains values for the feed template and building Articles.
    # Dates are included as datetimes and RFC 822 format strings so the context
    # can be used to fill out the feed template and populate Article models.
    now = timezone.now().replace(microsecond=0)
    return {
        "title": "Article title.",
        "url": "https://www.example.com/entry/",
        "date": now,
        "date_str": now.strftime("%a, %d %b %Y %H:%M:%S %z"),
        "identifier": "Article:Identifier",
        "author": "Article Author",
        "summary": "Article Summary",
        "tags": ["First", "Second"],
    }


def filter_title(name):
    return name.lower()


def filter_authors(names):
    return [name.lower() for name in names]


def filter_tags(names):
    skip = ["First"]
    return [name for name in names if name not in skip]


def test_title_hook(monkeypatch, feed_template, feed_context, settings):
    settings.FEEDS_FILTER_TITLE = "feeds.tests.loader.test_load_hooks.filter_title"

    def mock_return(feed):
        template = Template(feed_template)
        context = Context(feed_context)
        return template.render(context)

    monkeypatch.setattr(loader, "get_source", mock_return)
    feed = FeedFactory.create(enabled=True)
    loader.load_feed(feed)
    article = Article.objects.first()

    assert article.title == filter_title(feed_context["title"])


def test_authors_hook(monkeypatch, feed_template, feed_context, settings):
    settings.FEEDS_FILTER_AUTHORS = "feeds.tests.loader.test_load_hooks.filter_authors"

    def mock_return(feed):
        template = Template(feed_template)
        context = Context(feed_context)
        return template.render(context)

    monkeypatch.setattr(loader, "get_source", mock_return)
    feed = FeedFactory.create(enabled=True)
    loader.load_feed(feed)
    article = Article.objects.first()

    expected = filter_authors([feed_context["author"]])
    actual = [author.name for author in article.authors.all()]
    assert actual == expected


def test_tags_hook(monkeypatch, feed_template, feed_context, settings):
    settings.FEEDS_FILTER_TAGS = "feeds.tests.loader.test_load_hooks.filter_tags"

    def mock_return(feed):
        template = Template(feed_template)
        context = Context(feed_context)
        return template.render(context)

    monkeypatch.setattr(loader, "get_source", mock_return)
    feed = FeedFactory.create(enabled=True)
    loader.load_feed(feed)
    article = Article.objects.first()

    expected = filter_tags(feed_context["tags"])
    actual = [tag.name for tag in article.tags.all()]
    assert actual == expected
