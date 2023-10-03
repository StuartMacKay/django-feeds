from django.core.exceptions import ValidationError
from django.utils import timezone

import pytest

from feeds.models import Feed
from feeds.tests.factories import FeedFactory

pytestmark = pytest.mark.django_db


def test_schedule_invalid():
    with pytest.raises(ValidationError):
        FeedFactory(schedule="0 10, 12 * * *").full_clean()


def test_schedule_minutes_valid():
    FeedFactory(schedule="0 10 * * *").full_clean()
    FeedFactory(schedule="* 10 * * *").full_clean()


def test_schedule_minutes_invalid():
    with pytest.raises(ValidationError):
        FeedFactory(schedule="15 10 * * *").full_clean()


@pytest.mark.freeze_time
def test_feed_scheduled(freezer):
    feed = FeedFactory.create(enabled=True, schedule="0 10 * * *")
    freezer.move_to(timezone.now().replace(minute=0, hour=10))
    feeds = Feed.objects.scheduled_for(timezone.now())
    assert feed.pk in [feed.pk for feed in feeds]


@pytest.mark.freeze_time
def test_unscheduled_feed_skipped(monkeypatch, freezer):
    feed = FeedFactory.create(enabled=True, schedule="0 11 * * *")
    freezer.move_to(timezone.now().replace(minute=0, hour=10))
    feeds = Feed.objects.scheduled_for(timezone.now())
    assert feed.pk not in [feed.pk for feed in feeds]


@pytest.mark.freeze_time
def test_default_schedule_used(monkeypatch, freezer, settings):
    feed = FeedFactory.create(enabled=True, schedule="")
    settings.FEEDS_LOAD_SCHEDULE = "0 10 * * *"
    freezer.move_to(timezone.now().replace(minute=0, hour=10))
    feeds = Feed.objects.scheduled_for(timezone.now())
    assert feed.pk in [feed.pk for feed in feeds]
