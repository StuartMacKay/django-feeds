import logging

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.db import DataError
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

import tagulous.admin  # type: ignore

from feeds.models import Feed
from feeds.services import feeds

log = logging.getLogger(__name__)


class StatusFilter(admin.SimpleListFilter):
    title = _("Status")
    parameter_name = "status"

    ranges = {
        "1xx": (100, 200),
        "2xx": (200, 300),
        "3xx": (300, 400),
        "4xx": (400, 500),
        "5xx": (500, 600),
    }

    def lookups(self, request, model_admin):
        return (
            ("1xx", _("1xx")),
            ("2xx", _("2xx")),
            ("3xx", _("3xx")),
            ("4xx", _("4xx")),
            ("5xx", _("5xx")),
            ("null", _("Unknown")),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "null":
            return queryset.filter(status__isnull=True)
        elif value in self.ranges:
            begin, end = self.ranges[value]
            return queryset.filter(status__gte=begin, status__lt=end)
        elif value:
            return queryset.none()


class FailingFilter(admin.SimpleListFilter):
    title = _("Failing")
    parameter_name = "failing"

    def lookups(self, request, model_admin):
        return (
            ("0", _("No")),
            ("1", _("Yes")),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "0":
            return queryset.filter(failures=0)
        elif value == "1":
            return queryset.filter(failures__gt=0)
        elif value:
            return queryset.none()


class FeedForm(forms.ModelForm):
    class Meta:
        model = Feed
        fields = (
            "name",
            "source",
            "url",
            "categories",
            "enabled",
            "schedule",
            "auto_publish",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if url := self.data.get("url", self.initial.get("url")):
            validate_url = "https://validator.w3.org/feed/check.cgi?" + urlencode(
                {"url": url}
            )
            message = _('<a href="%s" target="_blank">Validate</a> the current url')
            self.fields["url"].help_text = mark_safe(message % validate_url)

    def clean_schedule(self):
        value = self.cleaned_data["schedule"]

        # Remove any extra spaces to reduce the chances that an invalid
        # crontab string will be entered.

        value = value.replace("  ", " ")
        value = value.replace(" ,", ",")
        value = value.replace(", ", ",")
        value = value.replace(" -", "-")
        value = value.replace("- ", "-")
        value = value.replace(" /", "/")
        value = value.replace("/ ", "/")

        return value.strip()


class FeedAdmin(ModelAdmin):
    list_display = (
        "name",
        "enabled",
        "auto_publish",
        "loaded",
        "failures",
        "status",
    )

    list_filter = (
        "categories",
        StatusFilter,
        FailingFilter,
        "enabled",
        "auto_publish",
    )

    search_fields = ("name",)

    readonly_fields = (
        "created",
        "modified",
        "loaded",
        "failures",
        "etag",
        "last_modified",
        "status",
    )

    actions = [
        "load_feed",
    ]

    form = FeedForm

    autocomplete_fields = ("source",)

    @admin.action(description=_("Load selected feeds"))
    def load_feed(modeladmin, request, queryset):  # noqa
        for feed in queryset:
            try:
                # force the feed to be loaded by resetting the fields
                # used to send the Last-Modified or ETag headers.

                feed.last_modified = None
                feed.etag = None

                # Call load_feed at the module level so this action
                # can be tested by mocking the function.

                result = feeds.load_feed(feed)
            except DataError:
                log.exception("Could not load feed", extra={"feed": feed.name})
                result = False

            if result:
                msg = _('The feed "%s" was loaded successfully.' % feed.name)
                messages.info(request, msg)
            else:
                msg = _('There was an error loading the feed "%s"' % feed.name)
                messages.error(request, msg)

    def get_queryset(self, request):
        return super(FeedAdmin, self).get_queryset(request)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return super().get_readonly_fields(request, obj)
        return []


tagulous.admin.register(Feed, FeedAdmin)
