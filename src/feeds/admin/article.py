from typing import Optional
from urllib.parse import quote

from django import forms
from django.contrib import admin, messages
from django.db import models
from django.forms import Textarea
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

import tagulous.admin  # type: ignore

from feeds.admin.prettifiers import prettify
from feeds.models import Article
from feeds.services.opengraph import load_tags


def retitle(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper


class IsArchivedFilter(admin.SimpleListFilter):
    title = _("Archived")
    parameter_name = "archived"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(archive_url__exact="")
        if self.value() == "no":
            return queryset.filter(archive_url__exact="")


class IsTaggedFilter(admin.SimpleListFilter):
    title = _("Tagged")
    parameter_name = "tagged"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Yes")),
            ("no", _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(tags=None)
        if self.value() == "no":
            return queryset.filter(tags=None)


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        search_url = "https://archive.md/" + quote(self.instance.url)
        message = _(
            "The link to the archived article. "
            '<a href="%s" target="_blank">Search</a> for an existing copy'
        )
        self.fields["archive_url"].help_text = mark_safe(message % search_url)


class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "date",
        "source",
        "published",
        "archived",
        "tagged",
    )

    list_filter = (
        ("publish", retitle("Published")),
        IsArchivedFilter,
        IsTaggedFilter,
        "categories",
    )

    search_fields = ("title",)

    ordering = ("-date",)

    actions = ["load_opengraph_tags"]

    readonly_fields = (
        "code",
        "pretty_data",
        "created",
        "modified",
    )

    autocomplete_fields = ("authors", "source", "tags")

    form = ArticleForm

    fields = (
        "title",
        "authors",
        "url",
        "source",
        "date",
        "tags",
        "categories",
        "publish",
        "code",
        "archive_url",
        "summary",
        "comment",
        "data",
        "pretty_data",
        "created",
        "modified",
    )

    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": "5", "cols": "80"})},
        models.JSONField: {"widget": Textarea(attrs={"rows": "10", "cols": "80"})},
    }

    @admin.display(boolean=True, description=_("Published"))
    def published(self, obj):
        return bool(obj.publish)

    @admin.display(boolean=True, description=_("Archived"))
    def archived(self, obj):
        return bool(obj.archive_url)

    @admin.display(boolean=True, description=_("Tagged"))
    def tagged(self, obj):
        return bool(obj.tags.all().count())

    @admin.display(description=_("Formatted"))
    def pretty_data(self, instance):
        return mark_safe(prettify(instance.data))

    @admin.action(description=_("Load Open Graph tags for selected Articles"))
    def load_opengraph_tags(modeladmin, request, queryset):
        for article in queryset:
            count: Optional[int] = load_tags(article)
            if count is None:
                messages.error(
                    request,
                    "Open Graph tags could not be loaded for '%s'" % article.title,
                )
            elif count:
                messages.info(
                    request,
                    "Open Graph tags for '%s' were loaded successfully" % article.title,
                )
            else:
                messages.warning(
                    request,
                    "Open Graph tags were not available for '%s'" % article.title,
                )

    def get_queryset(self, request):
        return (
            super(ArticleAdmin, self)
            .get_queryset(request)
            .select_related("source")
            .prefetch_related("authors", "categories", "tags")
        )

    def lookup_allowed(self, lookup: str, value: str) -> bool:
        if lookup in ("tags__slug__in", "source__slug__in", "authors__slug__in"):
            return True
        return super().lookup_allowed(lookup, value)


tagulous.admin.register(Article, ArticleAdmin)
