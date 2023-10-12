from django.template import Context, Template
from django.utils import timezone

import pytest

from feeds.models import Article
from feeds import loader
from feeds.tests.factories import (
    AliasFactory,
    ArticleFactory,
    FeedFactory,
    AuthorFactory,
    TagFactory,
)

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

    monkeypatch.setattr(loader, "get_source", mock_return)
    feed = FeedFactory.create(enabled=True)
    loader.load_feed(feed)
    articles = Article.objects.all()

    # Results contain added Article
    assert len(articles) == 1

    # Verify the rss attributes are set to the values from the feed
    # Ensure microseconds on the date the entry was published are set
    # to zero, rather than the value when the entry is saved in case
    # the date is used to see if an entry has changed when the feed
    # is next loaded.

    article = articles[0]

    assert article.title == feed_context["title"]
    assert article.url == feed_context["url"]
    assert article.date == feed_context["date"]
    assert article.date.microsecond == 0
    assert article.summary == feed_context["summary"]
    assert article.identifier == feed_context["identifier"]
    assert article.source == feed.source
    assert article.publish == feed.auto_publish

    # Verify the authors are added to the Article.
    assert article.authors.count() == 1
    actual = sorted([author.name for author in article.authors.all()])
    expected = [feed_context["author"]]
    assert actual == expected

    # Verify the tags are added to the Article.
    assert article.tags.count() == len(feed_context["tags"])
    actual = sorted([tag.name for tag in article.tags.all()])
    expected = sorted(feed_context["tags"])
    assert actual == expected

    # Verify the categories are added to the article
    assert article.categories.count() == feed.categories.count() != 0
    actual = sorted([category.name for category in article.categories.all()])
    expected = sorted([category.name for category in feed.categories.all()])
    assert actual == expected


def test_article_updated(monkeypatch, feed_template, feed_context):
    feed = FeedFactory.create(enabled=True, auto_publish=True)
    author = AuthorFactory.create(name=feed_context["author"])
    tags = [TagFactory.create(name=name) for name in feed_context["tags"]]
    params = {
        k: v
        for k, v in feed_context.items()
        if not k.endswith("date_str") and k not in ("author", "tags")
    }
    params["authors"] = [author.pk]
    params["tags"] = [tag.pk for tag in tags]
    existing = ArticleFactory.create(feed=feed, publish=feed.auto_publish, **params)

    feed_context["title"] = "Updated title"
    original_authors = [feed_context["author"]]
    feed_context["author"] = "Updated author"
    original_tags = feed_context["tags"]
    feed_context["tags"] = ["One", "Two"]

    feed.auto_publish = False
    feed.save()

    def mock_return(feed):
        template = Template(feed_template)
        context = Context(feed_context)
        return template.render(context)

    monkeypatch.setattr(loader, "get_source", mock_return)
    loader.load_feed(feed)
    articles = Article.objects.filter(modified__gt=existing.modified)

    # Results contains updated Article
    assert len(articles) == 1

    # The title of the entry was updated. All other attributes
    # remain unchanged.

    article = articles[0]

    assert article.modified > existing.modified
    assert article.title == feed_context["title"]
    assert article.url == feed_context["url"]
    assert article.date == feed_context["date"]
    assert article.date.microsecond == 0
    assert article.summary == feed_context["summary"]
    assert article.identifier == feed_context["identifier"]
    assert article.publish is True

    # The list of authors is not updated.
    assert article.authors.count() == 1
    actual = sorted([author.name for author in article.authors.all()])
    expected = sorted(original_authors)
    assert actual == expected

    # The list of tags is not updated.
    assert article.tags.count() == len(feed_context["tags"]) != 0
    actual = sorted([tag.name for tag in article.tags.all()])
    expected = sorted(original_tags)
    assert actual == expected


def test_article_author_alias(monkeypatch, feed_template, feed_context):
    alias = AliasFactory.create()
    feed = alias.feed
    author = alias.author

    feed_context["author"] = alias.name

    def mock_return(feed):
        template = Template(feed_template)
        context = Context(feed_context)
        return template.render(context)

    monkeypatch.setattr(loader, "get_source", mock_return)

    loader.load_feed(feed)

    article = Article.objects.all().first()

    assert article.authors.first() == author
