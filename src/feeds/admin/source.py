from typing import Optional

from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, register
from django.db import models
from django.forms import Textarea
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from feeds.admin.prettifiers import prettify
from feeds.models import Source
from feeds.services.opengraph import load_tags


@register(Source)
class SourceAdmin(ModelAdmin):
    list_display = (
        "name",
        "has_url",
        "has_description",
        "graphed",
    )

    search_fields = ("name",)

    actions = ["show_articles", "load_opengraph_tags"]

    readonly_fields = (
        "pretty_data",
        "created",
        "modified",
        "slug",
    )

    fields = (
        "name",
        "url",
        "description",
        "data",
        "pretty_data",
        "created",
        "modified",
        "slug",
    )

    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": "5", "cols": "80"})},
        models.JSONField: {"widget": Textarea(attrs={"rows": "10", "cols": "80"})},
    }

    @admin.display(boolean=True)
    def has_url(self, obj):
        return bool(obj.url)

    @admin.display(boolean=True)
    def has_description(self, obj):
        return bool(obj.description)

    @admin.display(boolean=True, description=_("Open Graph"))
    def graphed(self, obj):
        return bool(any([key for key in obj.data.keys() if key.startswith("og:")]))

    @admin.display(description=_("Formatted"))
    def pretty_data(self, instance):
        return mark_safe(prettify(instance.data))

    @admin.action(description=_("Show Articles for selected Sources"))
    def show_articles(modeladmin, request, queryset):
        url = "%s?source__slug__in=%s" % (
            reverse("admin:feeds_article_changelist"),
            ",".join([obj.slug for obj in queryset]),
        )
        return redirect(url)

    @admin.action(description=_("Load Open Graph data for selected Sources"))
    def load_opengraph_tags(modeladmin, request, queryset):
        for source in queryset:
            count: Optional[int] = load_tags(source)
            if count is None:
                messages.error(
                    request,
                    "Open Graph tags could not be loaded for '%s'" % source.name,
                )
            elif count:
                messages.info(
                    request,
                    "Open Graph tags for '%s' were loaded successfully" % source.name,
                )
            else:
                messages.warning(
                    request,
                    "Open Graph tags were not available for '%s'" % source.name,
                )
