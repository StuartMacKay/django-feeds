import logging
import re
from datetime import datetime
from html import unescape
from typing import List, Optional
from urllib.error import HTTPError, URLError

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils import timezone
from django.utils.text import slugify

import feedparser  # type: ignore
from dateutil.parser import parse as parse_date
from feedparser import FeedParserDict

from feeds.models import Alias, Article, Author, Feed

__all__ = ("load_feed", "get_user_agent")


validate_url = URLValidator()


def load_feeds() -> None:
    now = timezone.now()
    feeds = Feed.objects.scheduled_for(now)
    count = 0

    log = logging.getLogger(f"{__name__}.load_feeds")
    log.debug("Feeds scheduled", extra={"num_feeds": len(feeds)})

    for feed in feeds:
        if load_feed(feed):
            count += 1

    log.debug("Feeds loaded", extra={"num_feeds": count})


def load_feed(feed: Feed) -> bool:
    # The Last-Modified and ETag headers, from the previous fetch, are
    # sent when fetching a feed, so we only load entries if the feed
    # has been updated.

    # Since we do conditional fetches, the feeds can be updated frequently.
    # That lets avoid worrying about retries for network and remote
    # server errors since it will probably have been resolved by the
    # next fetch.

    log = logging.getLogger(f"{__name__}.load_feed")

    url = feed.url
    etag = feed.etag
    modified = feed.last_modified

    log.debug(
        "Feed request",
        extra={"feed": feed.name, "url": url, "last_modified": modified, "etag": etag},
    )

    feed.loaded = timezone.now()

    try:
        response = feedparser.parse(
            get_source(feed), agent=get_user_agent(), modified=modified, etag=etag
        )
    except (HTTPError, URLError):
        log.exception("Feed not fetched", extra={"feed": feed.name})
        feed.failures += 1
        feed.save()
        return False

    # The status field is not present in the response when a feed
    # is loaded from a string or a file.

    feed.status = response.get("status")

    value = response.headers.get("last-modified")
    modified = parse_date(value) if value else None
    etag = response.headers.get("etag")
    content_length = response.headers.get("content-length")
    num_entries = len(response.entries)

    log.debug(
        "Feed response",
        extra={
            "feed": feed.name,
            "status": feed.status,
            "last_modified": modified,
            "etag": etag,
            "content_length": content_length,
        },
    )

    # Strictly speaking, if the feed is unchanged then no XML was returned,
    # so we don't know if the feed is valid since nothing was parsed. However,
    # setting the valid flag to None implies some form of error occurred when
    # in fact the feed is operating normally.

    if feed.status == 304:
        log.debug("Feed is unchanged", extra={"feed": feed.name})
        feed.failures = 0
        feed.save()
        return False

    # Assume anything other than a 200 OK status at this point means that the
    # feed XML was not returned. This avoids confusingly reporting a parse
    # error if an HTML error page was returned, for example, if the feed url
    # changed. Note that the status will be None when running tests.

    if feed.status and feed.status != 200:
        log.error(
            "Feed not loaded",
            extra={
                "feed": feed.name,
                "status": feed.status,
                "num_entries": num_entries,
            },
        )
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
        log.error("Feed not parsed", exc_info=exc)
        feed.failures += 1
        feed.save()
        return False

    feed.etag = etag
    feed.last_modified = modified
    feed.failures = 0
    feed.save()

    num_created = 0

    for item in response.entries:
        values = {
            "identifier": get_identifier(item),
            "title": get_title(item),
            "url": get_url(item),
            "date": get_published(item),
            "summary": get_summary(item),
            "tags": get_tags(item),
        }

        # Simply skip over any items that are "badly formed". This is
        # preferable to simply letting exceptions be raised when saving
        # an Article as "badly formed" feed are not that unusual, so it's
        # better to ignore any missing data as it's likely to be present
        # at a later time, for example, an author forgets to add a title
        # to the article and publishes the post.

        required = ["identifier", "title", "url", "date"]

        if not all([v for k, v in values.items() if k in required]):
            continue

        article: Article = get_article(str(values.pop("identifier")))

        article.title = values["title"]  # type: ignore
        article.url = values["url"]  # type: ignore
        article.date = values["date"]  # type: ignore
        article.summary = values["summary"]  # type: ignore
        article.data["feed:tags"] = values["tags"]

        if article.pk is None:
            num_created += 1
            article.feed = feed
            article.source = feed.source
            article.publish = feed.auto_publish

        article.save()

        for category in feed.categories.all():
            article.categories.add(category)

        for author in get_authors(item, feed):
            article.authors.add(author)

    # Note the slight change in wording compared to when the feed status
    # was 304, see above. That makes it easier to tell what happened simply
    # by reading the message and not looking at the other values logged.

    message = "Feed was unchanged" if num_created == 0 else "Feed was loaded"

    log.debug(
        message,
        extra={
            "feed": feed.name,
            "num_entries": num_entries,
            "num_created": num_created,
        },
    )

    return True


def get_source(feed: Feed) -> str:
    # Feedparse can parse a file, url or string so this method exists to
    # allow an XML string to be injected for testing.
    return feed.url


def get_user_agent() -> str:
    return settings.FEEDS_USER_AGENT


def get_article(identifier: str) -> Article:
    if Article.objects.with_identifier(identifier).exists():
        article = Article.objects.with_identifier(identifier).get()
    else:
        article = Article(identifier=identifier)
    return article


def get_identifier(item: FeedParserDict) -> str:
    # Use the entry link as a last resort as the feed would likely fail
    # validation. This happens surprisingly often.
    return item.get("id", item.get("link", ""))


def get_url(item: FeedParserDict) -> str:
    try:
        if link := item.get("link", ""):
            validate_url(link)
    except ValidationError:
        link = ""

    return link


def get_title(item: FeedParserDict) -> str:
    # Some feeds, e.g. cartoons, might just contain an image so there is no title
    return normalize_title(unescape(item.get("title", "")))


def get_published(item: FeedParserDict) -> datetime:
    if date := item.get("published", None):
        date = parse_date(date)
    return date


def get_updated(item: FeedParserDict) -> datetime:
    if date := item.get("updated", None):
        date = parse_date(date)
    return date


def get_authors(item: FeedParserDict, feed: Feed) -> List[Author]:
    authors: List[Author] = []

    names = [
        author.get("name")  # noqa
        for author in item.get("authors", [])
        if author.get("name")  # noqa
    ]

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
                log = logging.getLogger(f"{__name__}.load_feed")
                log.exception("Multiple Authors found", extra={"author": name})
                author = Author.objects.with_slug(slug).first()

        if author:
            authors.append(author)

    return authors


def get_summary(item: FeedParserDict) -> str:
    return unescape(item.get("summary", ""))


def get_tags(item: FeedParserDict) -> List[str]:
    return sorted([tag.get("term") for tag in item.get("tags", []) if tag.get("term")])


def normalize_title(value: str) -> str:
    # Skip changes if the title is empty
    if not value:
        return value
    # Strip double-quotes around a title
    if value[0] == value[-1] == '"':
        value = value[1:-1]
    # Strip single-quotes around a title
    if value[0] == value[-1] == "'":
        value = value[1:-1]
    # Remove any trailing periods but leave an ellipsis alone
    if value[-1] == "." and value[-2] != ".":
        value = value[:-1]
    # Remove extra whitespace
    value = " ".join(value.split())
    # Put a space before and after a hyphen
    value = re.sub(r"(\w(\")?)-", r"\1 -", value)
    value = re.sub(r"-((\")?(\w))", r"- \1", value)
    # Put a space after a comma
    value = re.sub(r"(\w),(\w)", r"\1, \2", value)
    # Remove a space before a comma
    value = re.sub(r"(\w) ,", r"\1,", value)
    # Put a space before an opening bracket
    value = re.sub(r"(\w)\(", r"\1 (", value)
    # Put a space after a closing bracket
    value = re.sub(r"\)(\w)", r") \1", value)
    return value
