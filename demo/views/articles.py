from django.views import generic

from demo.paginators import DayPaginator
from demo.views.utils import shuffle
from feeds.models import Article, Tag


class ArticlesView(generic.ListView):
    template_name = "demo/articles.html"
    paginator_class = DayPaginator
    paginate_by = 7

    def get_queryset(self):
        return (
            Article.objects.published()
            .select_related("source")
            .prefetch_related("authors", "categories")
            .order_by("-date")
        )

    def get_groups_by_date(self, object_list):  # noqa
        groups = {}
        for article in object_list:
            date = article.date.date()
            groups.setdefault(date, [])
            groups[date].append(article)
        return groups

    def get_tags(self, object_list):  # noqa
        return shuffle(Tag.objects.for_articles(object_list).weighted())

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        objects = context["object_list"]
        context["tags"] = self.get_tags(objects)
        context["object_groups"] = self.get_groups_by_date(objects)
        return context
