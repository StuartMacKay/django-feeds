"""
URL Configuration for the demonstration site.

"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import RedirectView

import debug_toolbar  # type: ignore


urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("app_index"))),
    path("admin/", admin.site.urls),
    path("app/", include("app_project.urls")),
    path("__debug__/toolbar/", include(debug_toolbar.urls)),  # type: ignore
]
