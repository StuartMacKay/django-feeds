from django.urls import path

from feeds import views

app_name = 'feeds'

urlpatterns = [
    path(
        "article/",
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
        "source/popular/",
        views.PopularSourcesView.as_view(),
        name="sources-popular",
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
]
