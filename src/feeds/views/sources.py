import datetime as dt

from django.db.models import Count, F, Func, OuterRef, Prefetch, Subquery
from django.views import generic

from feeds.models import Article, Source
from feeds.paginator import AlphabetPaginator


class SourcesView(generic.ListView):
    template_name = "feeds/sources.html"
    paginator_class = AlphabetPaginator
    paginate_by = 25

    def get_queryset(self):
        return (
            Source.objects.all()
            .order_by("name")
            .annotate(article_count=Count("articles"))
            .prefetch_related(
                Prefetch(
                    "articles",
                    queryset=Article.objects.published().order_by("-date"),
                )
            )
        )


class PopularSourcesView(generic.ListView):
    template_name = "feeds/sources_popular.html"
    paginate_by = 25

    def get_queryset(self):
        # Recent is anything within the past four weeks
        date = dt.date.today() - dt.timedelta(days=28)
        # Call Count() indirectly to stop Django adding group by on 'pk'
        count_views = Func(F("views"), function="Sum")

        articles = Article.objects.published().since_date(date)
        referenced = articles.filter(source_id=OuterRef("pk"))
        views = referenced.annotate(clicks=count_views).values("views")

        sources = (
            Source.objects.all().annotate(views=Subquery(views)).order_by("-views")
        )

        return sources
