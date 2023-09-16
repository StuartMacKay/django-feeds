from django.contrib import admin

from app_project import models


@admin.register(models.Example)
class ExampleAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("name",)
