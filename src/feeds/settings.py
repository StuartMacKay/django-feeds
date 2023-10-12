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
# runs using the FEEDS_TASK_SCHEDULE setting which defaults to run every hour
# on the hour. Rather than fetch every feed each time you can set a schedule
# on individual feeds to reduce server load and bandwidth. If no schedule is
# set then the FEEDS_LOAD_SCHEDULE setting is used. When the celery task runs
# it compares the feed's schedule with the current time and if they match,
# the feed is loaded.
#
# IMPORTANT: the times represented by the FEEDS_TASK_SCHEDULE setting and the
# FEEDS_LOAD_SCHEDULE setting must coincide otherwise the feed will never be
# loaded. Since the celery task runs on the hour, you can add a little margin
# for error by setting the minute field for the feed schedule to "*" rather
# than "0". That way, if the task gets blocked temporarily as long as it gets
# executed in the next 59 minutes, the schedules will match and the feed will
# still be loaded.

FEEDS_TASK_SCHEDULE = os.environ.get("FEEDS_TASK_SCHEDULE", "0 * * * *")

if not croniter.is_valid(FEEDS_TASK_SCHEDULE):
    raise ImproperlyConfigured("FEEDS_TASK_SCHEDULE setting is not a valid cron entry")

FEEDS_LOAD_SCHEDULE = os.environ.get("FEEDS_LOAD_SCHEDULE", FEEDS_TASK_SCHEDULE)

if not croniter.is_valid(FEEDS_LOAD_SCHEDULE):
    raise ImproperlyConfigured("FEEDS_LOAD_SCHEDULE setting is not a valid cron entry")

# A default user-agent string that is used when loading RSS feeds. Some sites
# will return an error is the user-agent is not given.

FEEDS_USER_AGENT = os.environ.get("FEEDS_USER_AGENT", "Django Feeds")

# The following settings provide post-load hooks to process / filter the
# title, list of authors and list of tags for each entry in a feed.

# Python path to a function which can be used to modify a title before it
# is used to create or update an Article. For example remove any leading
# or trailing whitespace.
#
# FEEDS_FILTER_TITLE = "myapp.utils.filter_title"
#
# def filter_title(title: str) -> str:
#     return title.strip()

FEEDS_FILTER_TITLE = None

# Python path to a function which can be used to modify the list of authors
# of a post before they are added to an Article. For example, capitalize
# names.
#
# FEEDS_FILTER_AUTHORS = "myapp.utils.filter_authors"
#
# def filter_authors(names: List[str]) -> List[str]:
#     return [name.title() for name in names]

FEEDS_FILTER_AUTHORS = None

# Python path to a function which can be used to modify the list of tags
# for a post before they are added to an Article. For example, remove the
# default, "Uncategorized" tag found on many WordPress feeds.
#
# FEEDS_FILTER_TAGS = "myapp.utils.filter_tags"
#
# def filter_tags(names: List[str]) -> List[str]:
#     skip = ["uncategorized",]
#     return [name for name in names if name.lower() not in skip]

FEEDS_FILTER_TAGS = None

# ############
#   Tagulous
# ############

SERIALIZATION_MODULES = {
    "xml": "tagulous.serializers.xml_serializer",
    "json": "tagulous.serializers.json",
    "python": "tagulous.serializers.python",
    "yaml": "tagulous.serializers.pyyaml",
}
