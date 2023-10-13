from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin, helpers, register
from django.contrib.admin.utils import model_ngettext
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from feeds.models import Author


@register(Author)
class AuthorAdmin(ModelAdmin):
    list_display = ("name", "slug", "articles")
    search_fields = ("name",)

    fields = (
        "name",
        "slug",
        "description",
        "created",
        "modified",
    )

    readonly_fields = (
        "created",
        "modified",
    )

    actions = ("merge_authors", "show_articles")

    @admin.display(description=_("Articles"))
    def articles(self, obj):
        return obj.count

    @admin.action(description=_("Merge selected authors"))
    def merge_authors(modeladmin, request, queryset):
        if request.POST.get("post"):
            selected = Author.objects.get(pk=request.POST["selected"])

            for obj in queryset:
                if obj.pk == selected.pk:
                    continue
                for article in obj.articles.all():
                    article.authors.remove(obj)
                    article.authors.add(selected)
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
            "title": _("Merge authors"),
            "queryset": queryset,
            "opts": modeladmin.model._meta,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "media": modeladmin.media,
        }

        return render(request, "admin/merge_authors.html", context=context)

    @admin.action(description=_("Show Articles for selected Authors"))
    def show_articles(modeladmin, request, queryset):
        url = "%s?authors__slug__in=%s" % (
            reverse("admin:feeds_article_changelist"),
            ",".join([obj.slug for obj in queryset]),
        )
        return redirect(url)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super()
            .get_queryset(request)
            .prefetch_related("articles")
            .annotate(count=Count("articles"))
        )
