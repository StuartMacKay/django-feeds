from django.urls import path

"""
URL Configuration for the demonstration site.

"""
from django.contrib import admin
from django.urls import include, path

import debug_toolbar  # type: ignore

from demo import views

urlpatterns = [
    path(
        "",
        views.ArticlesView.as_view(),
        name="articles",
    ),
    path(
        "article/click/",
        views.ArticleClickView.as_view(),
        name="article-click",
    ),
    path(
        "article/<slug:code>/",
        views.ArticleView.as_view(),
        name="article",
    ),
    path(
        "author/",
        views.AuthorsView.as_view(),
        name="authors",
    ),
    path(
        "author/<slug:slug>/",
        views.AuthorView.as_view(),
        name="author",
    ),
    path(
        "source/",
        views.SourcesView.as_view(),
        name="sources",
    ),
    path(
        "source/<slug:slug>/",
        views.SourceView.as_view(),
        name="source",
    ),
    path(
        "tag/",
        views.TagsView.as_view(),
        name="tags",
    ),
    path(
        "tag/<slug:slug>/",
        views.TagView.as_view(),
        name="tag",
    ),
    path(
        "tag/<slug:slug>/author/<slug:author>/",
        views.TagView.as_view(),
        name="tag-author",
    ),
    path(
        "tag/<slug:slug>/source/<slug:source>/",
        views.TagView.as_view(),
        name="tag-source",
    ),
    path("admin/", admin.site.urls),
    path("__debug__/toolbar/", include(debug_toolbar.urls)),  # type: ignore
]
