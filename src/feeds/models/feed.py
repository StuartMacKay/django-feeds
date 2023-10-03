import datetime as dt
from typing import List

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

import tagulous  # type: ignore
from croniter import croniter
from django_extensions.db.models import TimeStampedModel


def validate_crontab(value):
    if not croniter.is_valid(value):
        raise ValidationError(
            _('"%(value)s" is not a valid crontab entry'),
            params={"value": value},
        )

    minutes = value.split()[0]

    if minutes != "0" and minutes != "*":
        raise ValidationError(
            _(
                "The celery task to load feeds runs every hour on the hour"
                "so the minutes field (the first) must be set to '0' or '*'"
            )
        )


class FeedQuerySet(models.QuerySet):
    def disabled(self) -> "FeedQuerySet":
        return self.filter(enabled=False)

    def enabled(self) -> "FeedQuerySet":
        return self.filter(enabled=True)

    def scheduled_for(self, timestamp: dt.datetime) -> List["Feed"]:
        feeds: List["Feed"] = []
        for feed in Feed.objects.enabled():
            schedule: str = feed.schedule or settings.FEEDS_LOAD_SCHEDULE
            if croniter.match(schedule, timestamp):
                feeds.append(feed)
        return feeds


FeedManager = models.Manager.from_queryset(FeedQuerySet)  # type: ignore


class Feed(TimeStampedModel):  # type: ignore
    class Meta:
        verbose_name = _("Feed")
        verbose_name_plural = _("Feeds")

    name = models.CharField(
        verbose_name=_("Name"),
        help_text=_("The name of the feed"),
        max_length=100,
    )

    source = models.ForeignKey(
        to="feeds.Source",
        on_delete=models.PROTECT,
        verbose_name=_("Source"),
        help_text=_("The web site which hosts the feed"),
    )

    url = models.URLField(
        verbose_name=_("URL"),
        help_text=_("The URL for the RSS feed (RSS or Atom)"),
    )

    categories = tagulous.models.TagField(
        verbose_name=_("Categories"),
        help_text=_("The categories of articles published by the feed"),
        to="feeds.Category",
        blank=True,
    )

    enabled = models.BooleanField(
        verbose_name=_("Enabled"),
        help_text=_("Enable loading of the RSS feed"),
        default=False,
    )

    schedule = models.CharField(
        validators=[validate_crontab],
        verbose_name=_("Schedule"),
        help_text=_(
            "Crontab entry which describe the times the feed will be downloaded."
            "Leave blank to use the default schedule defined for all feeds."
        ),
        max_length=100,
        blank=True,
    )

    auto_publish = models.BooleanField(
        verbose_name=_("Auto Publish"),
        help_text=_("Automatically publish Articles when added from an RSS Feed"),
        default=False,
    )

    load_tags = models.BooleanField(
        verbose_name=_("Load Tags"),
        help_text=_("Add the tags from the Feed when an Article is added"),
        default=True,
    )

    loaded = models.DateTimeField(
        verbose_name=_("Loaded"),
        help_text=_("The date that the RSS feed was last loaded"),
        null=True,
        blank=True,
    )

    failures = models.IntegerField(
        verbose_name=_("Failures"),
        help_text=_("The number of consecutive times a feed has failed to load."),
        default=0,
    )

    status = models.IntegerField(
        verbose_name=_("Status"),
        help_text=_("The HTTP status code from the last time the feed was fetched"),
        null=True,
        blank=True,
    )

    etag = models.CharField(
        verbose_name=_("ETag"),
        help_text=_("The Etag header from the RSS feed (Atom feeds only)"),
        max_length=100,
        null=True,
        blank=True,
    )

    last_modified = models.DateTimeField(
        verbose_name=_("Last Modified"),
        help_text=_("The last-modified header from the RSS feed"),
        null=True,
        blank=True,
    )

    objects = FeedManager()  # type: ignore

    def __str__(self):
        return self.name
