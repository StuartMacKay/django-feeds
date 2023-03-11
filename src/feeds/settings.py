"""
Django settings for django-feeds.

"""
import os

from django.core.exceptions import ImproperlyConfigured

from croniter import croniter


# #########
#   FEEDS
# #########

# Feeds are loaded using a celery task. You can schedule how often this task
# runs using the FEED_TASK_SCHEDULE setting which defaults to run every hour
# on the hour. Rather than fetch every feed each time you can set a schedule
# on individual feeds to reduce server load and bandwidth. If no schedule is
# set then the LOAD_FEED_SCHEDULE setting is used. When the celery task runs
# it compares the feed's schedule with the current time and if they match,
# the feed is loaded.
#
# IMPORTANT: the times represented by the FEED_TASK_SCHEDULE setting and the
# FEED_LOAD_SCHEDULE setting must coincide otherwise the feed will never be
# loaded. Since the celery task runs on the hour, you can add a little margin
# for error by setting the minute field for the feed schedule to "*" rather
# than "0". That way, if the task gets blocked temporarily as long as it gets
# executed in the next 59 minutes, the schedules will match and the feed will
# still be loaded.

FEED_TASK_SCHEDULE = os.environ.get("FEED_TASK_SCHEDULE", "0 * * * *")

if not croniter.is_valid(FEED_TASK_SCHEDULE):
    raise ImproperlyConfigured("FEED_TASK_SCHEDULE setting is not a valid cron entry")

FEED_LOAD_SCHEDULE = os.environ.get("FEED_LOAD_SCHEDULE", FEED_TASK_SCHEDULE)

if not croniter.is_valid(FEED_LOAD_SCHEDULE):
    raise ImproperlyConfigured("FEED_LOAD_SCHEDULE setting is not a valid cron entry")

# Setting for loading Open Graph data for Articles created when a Feed
# is loaded. Using a setting makes it easy to turn off during testing.

LOAD_OPEN_GRAPH_DATA = True

# A default user-agent string that is used when loading RSS feeds. Some sites
# will return an error is the user-agent is not given.

FEEDS_USER_AGENT = os.environ.get("FEEDS_USER_AGENT", "Django Feeds")

# ############
#   Tagulous
# ############

SERIALIZATION_MODULES = {
    "xml": "tagulous.serializers.xml_serializer",
    "json": "tagulous.serializers.json",
    "python": "tagulous.serializers.python",
    "yaml": "tagulous.serializers.pyyaml",
}
