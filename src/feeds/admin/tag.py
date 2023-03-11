from django.contrib import admin, messages
from django.contrib.admin import helpers, register
from django.contrib.admin.utils import model_ngettext
from django.db import models
from django.db.models import Count, QuerySet
from django.forms import Textarea
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from feeds.models import Tag


class ArticleCountFilter(admin.SimpleListFilter):
    title = _("No. of Articles")
    parameter_name = "number_of_articles"

    def lookups(self, request, model_admin):
        return (
            (0, _("0")),
            (1, _("1")),
            (2, _("2")),
            (3, _("3")),
        )

    def queryset(self, request, queryset):
        if value := self.value():
            try:
                return queryset.filter(count=int(value))
            except ValueError:
                return queryset.none()
        return queryset


@register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "has_summary", "articles")

    list_filter = (ArticleCountFilter,)

    search_fields = ("name",)

    fields = (
        "name",
        "slug",
        "summary",
        "description",
        "related",
        "created",
        "modified",
    )

    readonly_fields = ("created", "modified")

    actions = ["merge_tags", "show_articles"]

    autocomplete_fields = ("related",)

    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": "5", "cols": "80"})},
    }

    @admin.display(boolean=True, description=_("Has Summary"))
    def has_summary(self, obj):
        return bool(obj.summary)

    @admin.display(description=_("Articles"))
    def articles(self, obj):
        return obj.count

    @admin.action(description=_("Merge selected Tags"))
    def merge_tags(modeladmin, request, queryset):
        if request.POST.get("post"):
            selected = Tag.objects.get(pk=request.POST["selected"])

            for obj in queryset:
                if obj.pk == selected.pk:
                    continue
                for article in obj.article_set.all():
                    article.tags.remove(obj)
                    article.tags.add(selected)
                obj.delete()

            if count := queryset.count():
                modeladmin.message_user(
                    request,
                    _("Successfully merged %(count)d %(items)s.")
                    % {"count": count, "items": model_ngettext(modeladmin.opts, count)},
                    messages.SUCCESS,
                )
            return None

        context = {
            **modeladmin.admin_site.each_context(request),
            "title": _("Merge Tags"),
            "queryset": queryset,
            "opts": modeladmin.model._meta,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "media": modeladmin.media,
        }

        return render(request, "admin/merge_tags.html", context=context)

    @admin.action(description=_("Show Articles for selected Tags"))
    def show_articles(modeladmin, request, queryset):
        url = "%s?tags__slug__in=%s" % (
            reverse("admin:feeds_article_changelist"),
            ",".join([obj.slug for obj in queryset]),
        )
        return redirect(url)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .prefetch_related("article_set")
            .annotate(count=Count("article"))
        )
