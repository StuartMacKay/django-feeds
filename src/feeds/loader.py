import logging
from datetime import datetime
from html import unescape
from typing import List, Optional
from urllib.error import HTTPError, URLError

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.template.defaultfilters import truncatechars
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.text import slugify

import feedparser  # type: ignore
from dateutil.parser import parse as parse_date
from feedparser import FeedParserDict

from feeds.models import Alias, Article, Author, Feed, Tag

__all__ = ("load_feed", "get_user_agent")


validate_url = URLValidator()
log = logging.getLogger(__name__)


def load_feeds() -> None:
    now = timezone.now()
    feeds = Feed.objects.scheduled_for(now)

    log.info("Feeds scheduled")

    for feed in feeds:
        load_feed(feed)

    log.info("Feeds loaded")


def load_feed(feed: Feed) -> bool:
    # The Last-Modified and ETag headers, from the previous fetch, are
    # sent when fetching a feed, so we only load entries if the feed
    # has been updated.

    # Since we do conditional fetches, the feeds can be updated frequently.
    # That lets avoid worrying about retries for network and remote
    # server errors since it will probably have been resolved by the
    # next fetch.

    url = feed.url
    etag = feed.etag
    modified = feed.last_modified

    log.info(
        "Feed request",
        extra={"feed": feed.name, "url": url, "last_modified": modified, "etag": etag},
    )

    try:
        response = feedparser.parse(
            get_source(feed), agent=get_user_agent(), modified=modified, etag=etag
        )
    except (HTTPError, URLError):
        # Update the feed status to a generic request error so it always reflects
        # the state of the latest request.
        log.exception("Feed not fetched", extra={"feed": feed.name})
        feed.status = 400
        feed.failures += 1
        feed.save()
        return False

    # The status field is not present in the response when a feed
    # is loaded from a string or a file.

    status = response.get("status")
    value = response.headers.get("last-modified")
    modified = parse_date(value) if value else None
    etag = response.headers.get("etag")
    content_length = response.headers.get("content-length")

    log.info(
        "Feed response",
        extra={
            "feed": feed.name,
            "status": status,
            "last_modified": modified,
            "etag": etag,
            "content_length": content_length,
            "href": getattr(response, "href", ""),
        },
    )

    if status == 304:
        # Explicitly log when a feed is unchanged, so we know everything was ok
        log.info("Feed is unchanged", extra={"feed": feed.name})
        feed.status = status
        feed.failures = 0
        feed.save()
        return False

    # Assume anything other than a 200 OK status at this point means that the
    # feed XML was not returned. This avoids confusingly reporting a parse
    # error if an HTML error page was returned, for example, if the feed url
    # changed.
    #
    # IMPORTANT: the status will be None when running tests.

    if status and status != 200:
        log.error("Feed not loaded", extra={"feed": feed.name})
        feed.status = status
        feed.failures += 1
        feed.save()
        return False

    # One source of feed parsing failures is non-printing characters, which
    # presumably were the copy and pasted into the post when it was created.
    # We don't want abandon the load at this point as it might be something
    # that the feed author can correct and since we're having trouble other
    # people are as well, so it's worth contacting them over this.

    if response.bozo:
        exc = response.get("bozo_exception", None)
        log.error("Feed not parsed", exc_info=exc, extra={"feed": feed.name})
        feed.status = status
        feed.failures += 1
        feed.save()
        return False

    feed.status = status
    feed.etag = etag
    feed.last_modified = modified
    feed.loaded = timezone.now()
    feed.failures = 0
    feed.save()

    for item in response.entries:
        create_or_update_article(
            feed,
            get_identifier(item),
            get_title(item),
            get_summary(item),
            get_url(item),
            get_published(item),
            get_names(item),
            get_tags(item),
        )

    log.info("Feed was loaded", extra={"feed": feed.name})

    return True


def get_source(feed: Feed) -> str:
    # Feedparse can parse a file, url or string so this method exists to
    # allow an XML string to be injected for testing.
    return feed.url


def get_user_agent() -> str:
    return settings.FEEDS_USER_AGENT


def get_identifier(item: FeedParserDict) -> str:
    # Use the entry link as a last resort as the feed would likely fail
    # validation. This happens surprisingly often.
    return item.get("id", item.get("link", ""))


def get_title(item: FeedParserDict) -> str:
    # Some feeds, e.g. cartoons, might just contain an image so there is no title
    title = unescape(item.get("title", ""))
    if getattr(settings, "FEEDS_FILTER_TITLE", None):
        processor = import_string(settings.FEEDS_FILTER_TITLE)
        title = processor(title)
    return title


def get_url(item: FeedParserDict) -> str:
    try:
        if link := item.get("link", ""):
            validate_url(link)
    except ValidationError:
        link = ""

    return link


def get_published(item: FeedParserDict) -> datetime:
    if date := item.get("published", None):
        date = parse_date(date)
    return date


def get_updated(item: FeedParserDict) -> datetime:
    if date := item.get("updated", None):
        date = parse_date(date)
    return date


def get_summary(item: FeedParserDict) -> str:
    return unescape(item.get("summary", ""))


def get_names(item: FeedParserDict) -> List[str]:
    names: List[str] = [
        author.get("name")  # noqa
        for author in item.get("authors", [])
        if author.get("name")  # noqa
    ]
    if getattr(settings, "FEEDS_FILTER_AUTHORS", None):
        processor = import_string(settings.FEEDS_FILTER_AUTHORS)
        names = processor(names)
    return names


def get_tags(item: FeedParserDict) -> List[str]:
    tags = sorted([tag.get("term") for tag in item.get("tags", []) if tag.get("term")])
    if getattr(settings, "FEEDS_FILTER_TAGS", None):
        processor = import_string(settings.FEEDS_FILTER_TAGS)
        tags = processor(tags)
    return tags


def article_with_identifier(identifier: str) -> tuple[Article, bool]:
    if Article.objects.with_identifier(identifier).exists():
        article = Article.objects.with_identifier(identifier).get()
        created = False
    else:
        article = Article(identifier=identifier)
        created = True
    return article, created


def authors_for_names(feed: Feed, names: List[str]) -> List[int]:
    authors: List[int] = []

    for name in names:
        author: Optional[Author]
        alias: Optional[Alias] = Alias.objects.filter(name=name, feed=feed).first()

        if alias:
            author = alias.author
        else:
            slug: str = slugify(name)

            try:
                # Check if the Author exists using the slug. That way case changes
                # in the Author's name do not result in multiple authors.
                author, created = Author.objects.get_or_create(
                    slug=slug, defaults={"name": name}
                )
            except Author.MultipleObjectsReturned:
                log.exception(
                    "Multiple Authors found", extra={"feed": feed.name, "author": name}
                )
                author = Author.objects.with_slug(slug).first()

        if author:
            authors.append(author.pk)

    return authors


def tags_for_names(names: List[str]) -> List[int]:
    tags: List[int] = []
    for name in names:
        tag, created = Tag.objects.get_or_create(name=name, slug=slugify(name))
        tags.append(tag.pk)
    return tags


def create_or_update_article(
    feed: Feed,
    identifier: str,
    title: str,
    summary: str,
    url: str,
    published: datetime,
    authors: List[str],
    tags: List[str],
) -> None:
    # Simply skip over any items that are "badly formed". This is
    # preferable to simply letting exceptions be raised when saving
    # an Article as "badly formed" feed are not that unusual, so it's
    # better to ignore any missing data as it's likely to be present
    # at a later time, for example, an author forgets to add a title
    # to the article and publishes the post.

    if not all((identifier, title, url, published)):
        log.info(
            "Article incomplete",
            extra={
                "feed": feed.name,
                "identifier": truncatechars(identifier, 20),
                "title": truncatechars(title, 20),
                "url": truncatechars(url, 20),
                "date": published,
            },
        )
        return

    article: Article
    created: bool

    article, created = article_with_identifier(identifier)

    article.title = title
    article.url = url
    article.date = published
    article.summary = summary

    if created:
        article.feed = feed
        article.source = feed.source
        article.publish = feed.auto_publish

    article.save()

    if created:
        # Only set the authors, categories and tags for new Articles.
        # That way any edits, for example, adding the author of a guest
        # post, are not discarded.

        article.authors.add(*authors_for_names(feed, authors))
        article.categories.add(*feed.categories.all())
        if feed.load_tags:
            article.tags.add(*tags_for_names(tags))

    if created:
        log.info(
            "Article added",
            extra={"feed": feed.name, "title": truncatechars(title, 20)},
        )
    else:
        log.info(
            "Article updated",
            extra={"feed": feed.name, "title": truncatechars(title, 20)},
        )
