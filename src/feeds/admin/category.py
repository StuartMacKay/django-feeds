from django.contrib import admin

import tagulous  # type: ignore

from feeds.models import Category


class CategoryAdmin(admin.ModelAdmin):

    list_display = ("name", "count", "protected")
    search_fields = ("name",)


tagulous.admin.register(Category, CategoryAdmin)
