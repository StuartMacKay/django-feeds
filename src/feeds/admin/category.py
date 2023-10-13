from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

import tagulous  # type: ignore

from feeds.admin.prettifiers import prettify
from feeds.models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "count", "protected")
    search_fields = ("name",)

    readonly_fields = ("pretty_data",)

    @admin.display(description=_("Formatted"))
    def pretty_data(self, instance):
        return mark_safe(prettify(instance.data))


tagulous.admin.register(Category, CategoryAdmin)
