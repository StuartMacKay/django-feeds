from django.db.models import Count, Prefetch
from django.views import generic

from demo.paginators import AlphabetPaginator
from feeds.models import Article, Author


class AuthorsView(generic.ListView):
    template_name = "demo/authors.html"
    paginator_class = AlphabetPaginator
    paginate_by = 25

    def get_queryset(self):
        return (
            Author.objects.published()
            .order_by("name")
            .annotate(article_count=Count("articles"))
            .prefetch_related(
                Prefetch("articles", queryset=Article.objects.all().order_by("-date"))
            )
        )
