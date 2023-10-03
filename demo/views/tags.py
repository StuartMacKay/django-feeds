from django.db.models import Count, Prefetch
from django.views import generic

from demo.paginators import AlphabetPaginator
from feeds.models import Article, Tag


class TagsView(generic.ListView):
    template_name = "demo/tags.html"
    paginator_class = AlphabetPaginator
    paginate_by = 25

    def get_queryset(self):
        return (
            Tag.objects.all()
            .order_by("name")
            .annotate(article_count=Count("article"))
            .prefetch_related(
                Prefetch(
                    "article_set", queryset=Article.objects.all().order_by("-date")
                )
            )
        )
