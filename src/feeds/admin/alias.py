from django.contrib.admin import ModelAdmin, register

from feeds.models import Alias


@register(Alias)
class AliasAdmin(ModelAdmin):
    list_display = ("name", "author", "feed")
    search_fields = ("name", "author__name", "feed__name")
    autocomplete_fields = ("author", "feed")
    readonly_fields = ("created", "modified")
    fields = ("name", "author", "feed", "created", "modified")
