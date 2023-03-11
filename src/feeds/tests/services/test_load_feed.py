from django.template import Context, Template
from django.utils import timezone

import pytest

from feeds.models import Article
from feeds.services import feeds
from feeds.services.feeds import normalize_title
from feeds.tests.factories import AliasFactory, ArticleFactory, FeedFactory

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


def test_article_added(monkeypatch, feed_template, feed_context):
    # feedparser can parse a file, url or string so we can use the get_url()
    # function in the feeds module to inject a string instead of the Blog's
    # url and get feedparser to parse it and return the entries.

    def mock_return(feed):
        template = Template(feed_template)
        context = Context(feed_context)
        return template.render(context)

    monkeypatch.setattr(feeds, "get_source", mock_return)
    feed = FeedFactory.create(enabled=True)
    feeds.load_feed(feed)
    articles = Article.objects.all()

    # Results contain added Article
    assert len(articles) == 1

    # Verify the rss attributes are set to the values from the feed
    # Ensure microseconds on the date the entry was published are set
    # to zero, rather than the value when the entry is saved in case
    # the date is used to see if an entry has changed when the feed
    # is next loaded.

    article = articles[0]

    assert article.title == normalize_title(feed_context["title"])
    assert article.authors.first().name == feed_context["author"]
    assert article.url == feed_context["url"]
    assert article.date == feed_context["date"]
    assert article.date.microsecond == 0
    assert article.summary == feed_context["summary"]
    assert article.identifier == feed_context["identifier"]
    assert article.source == feed.source
    assert article.publish == feed.auto_publish

    # Verify the tags are added to the JSON data field. Only one
    # tag is used to keep the feed template and this test, simple.
    assert article.data["feed:tags"] == feed_context["tags"]

    # Verify the categories are added to the article
    assert article.categories.count() == feed.categories.count() != 0
    assert article.categories.first() == feed.categories.first()


def test_article_updated(monkeypatch, feed_template, feed_context):
    feed = FeedFactory.create(enabled=True, auto_publish=True)
    params = {
        k: v
        for k, v in feed_context.items()
        if not k.endswith("date_str") and k not in ("author", "tags")
    }
    existing = ArticleFactory.create(feed=feed, publish=feed.auto_publish, **params)

    feed_context["title"] = "Updated title"
    updated_title = feed_context["title"]

    feed.auto_publish = False
    feed.save()

    def mock_return(feed):
        template = Template(feed_template)
        context = Context(feed_context)
        return template.render(context)

    monkeypatch.setattr(feeds, "get_source", mock_return)
    feeds.load_feed(feed)
    articles = Article.objects.filter(modified__gt=existing.modified)

    # Results contains updated Article
    assert len(articles) == 1

    # The title of the entry was updated. All other attributes
    # remain unchanged.

    article = articles[0]

    assert article.modified > existing.modified
    assert article.title == updated_title
    assert article.url == feed_context["url"]
    assert article.date == feed_context["date"]
    assert article.date.microsecond == 0
    assert article.summary == feed_context["summary"]
    assert article.identifier == feed_context["identifier"]
    assert article.publish is True


def test_article_author_alias(monkeypatch, feed_template, feed_context):
    alias = AliasFactory.create()
    feed = alias.feed
    author = alias.author

    feed_context["author"] = alias.name

    def mock_return(feed):
        template = Template(feed_template)
        context = Context(feed_context)
        return template.render(context)

    monkeypatch.setattr(feeds, "get_source", mock_return)

    feeds.load_feed(feed)

    article = Article.objects.all().first()

    assert article.authors.first() == author


titles = [
    (" Hello World", "Hello World"),  # leading space
    ("  Hello World", "Hello World"),  # multiple leading spaces
    ("Hello World ", "Hello World"),  # trailing space
    ("Hello World  ", "Hello World"),  # multiple trailing spaces
    ("Hello World.", "Hello World"),  # trailing period
    ("Hello World...", "Hello World..."),  # trailing ellipsis
    ("Hello- World", "Hello - World"),  # no space before hyphen
    ("Hello -World", "Hello - World"),  # no space after hyphen
    ("Hello , World", "Hello, World"),  # space before comma
    ("Hello,World", "Hello, World"),  # no space after comma
    ("Hello(World)", "Hello (World)"),  # no space before bracket
    ("(Hello)World", "(Hello) World"),  # no space after bracket
]


@pytest.mark.parametrize("before, expected", titles)
def test_normalise_title(before, expected):
    after = feeds.normalize_title(before)
    assert after == expected
