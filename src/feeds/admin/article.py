from urllib.parse import quote

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.utils import model_ngettext
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.db import models
from django.forms import Textarea
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

import tagulous.admin  # type: ignore

from feeds.admin.prettifiers import prettify
from feeds.models import Article, Category, Tag


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


class AddTagsForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        label="Add the following tags",
        queryset=Tag.objects.all(),
        widget=AutocompleteSelectMultiple(Article._meta.get_field("tags"), admin.site),
    )


class RemoveTagsForm(forms.Form):
    tags = forms.ModelMultipleChoiceField(
        label="Remove the following tags",
        queryset=Tag.objects.all(),
        widget=AutocompleteSelectMultiple(Article._meta.get_field("tags"), admin.site),
    )


class AddCategoriesForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        label="Add the following categories",
        queryset=Category.objects.all(),
        widget=AutocompleteSelectMultiple(
            Article._meta.get_field("categories"), admin.site
        ),
    )


class RemoveCategoriesForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(
        label="Remove the following categories",
        queryset=Category.objects.all(),
        widget=AutocompleteSelectMultiple(
            Article._meta.get_field("categories"), admin.site
        ),
    )


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

    actions = [
        "add_tags",
        "remove_tags",
        "add_categories",
        "remove_categories",
    ]

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

    @admin.action(description=_("Add Tags to selected Articles"))
    def add_tags(modeladmin, request, queryset):
        if request.POST.get("post"):
            tags = request.POST.getlist("tags")

            for article in queryset:
                article.tags.add(*tags)

            if count := queryset.count():
                modeladmin.message_user(
                    request,
                    _("Successfully added tags to %(count)d %(items)s.")
                    % {"count": count, "items": model_ngettext(modeladmin.opts, count)},
                    messages.SUCCESS,
                )
            return None

        context = {
            **modeladmin.admin_site.each_context(request),
            "title": _("Add Tags"),
            "queryset": queryset,
            "opts": modeladmin.model._meta,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "media": modeladmin.media,
            "form": AddTagsForm(),
        }

        return render(request, "admin/add_tags.html", context=context)

    @admin.action(description=_("Remove Tags from selected Articles"))
    def remove_tags(modeladmin, request, queryset):
        if request.POST.get("post"):
            tags = request.POST.getlist("tags")

            for article in queryset:
                article.tags.remove(*tags)

            if count := queryset.count():
                modeladmin.message_user(
                    request,
                    _("Successfully removed tags from %(count)d %(items)s.")
                    % {"count": count, "items": model_ngettext(modeladmin.opts, count)},
                    messages.SUCCESS,
                )
            return None

        context = {
            **modeladmin.admin_site.each_context(request),
            "title": _("Remove Tags"),
            "queryset": queryset,
            "opts": modeladmin.model._meta,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "media": modeladmin.media,
            "form": RemoveTagsForm(),
        }

        return render(request, "admin/remove_tags.html", context=context)

    @admin.action(description=_("Add Categories to selected Articles"))
    def add_categories(modeladmin, request, queryset):
        if request.POST.get("post"):
            pks = request.POST.getlist("categories")
            categories = Category.objects.filter(pk__in=pks)

            for article in queryset:
                article.categories.add(*categories)

            if count := queryset.count():
                modeladmin.message_user(
                    request,
                    _("Successfully added categories to %(count)d %(items)s.")
                    % {"count": count, "items": model_ngettext(modeladmin.opts, count)},
                    messages.SUCCESS,
                )
            return None

        context = {
            **modeladmin.admin_site.each_context(request),
            "title": _("Add Categories"),
            "queryset": queryset,
            "opts": modeladmin.model._meta,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "media": modeladmin.media,
            "form": AddCategoriesForm(),
        }

        return render(request, "admin/add_categories.html", context=context)

    @admin.action(description=_("Remove Categories from selected Articles"))
    def remove_categories(modeladmin, request, queryset):
        if request.POST.get("post"):
            pks = request.POST.getlist("categories")
            categories = Category.objects.filter(pk__in=pks)

            for article in queryset:
                article.categories.remove(*categories)

            if count := queryset.count():
                modeladmin.message_user(
                    request,
                    _("Successfully removed categories from %(count)d %(items)s.")
                    % {"count": count, "items": model_ngettext(modeladmin.opts, count)},
                    messages.SUCCESS,
                )
            return None

        context = {
            **modeladmin.admin_site.each_context(request),
            "title": _("Remove Categories"),
            "queryset": queryset,
            "opts": modeladmin.model._meta,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "media": modeladmin.media,
            "form": RemoveCategoriesForm(),
        }

        return render(request, "admin/remove_categories.html", context=context)

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
