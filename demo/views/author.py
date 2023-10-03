from typing import List

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from demo.views.utils import shuffle
from feeds.models import Article, Author, Tag


class AuthorView(generic.ListView):
    template_name = "demo/author.html"
    paginate_by = 20

    def get_queryset(self):
        return (
            Article.objects.published()
            .by_author(self.kwargs["slug"])
            .select_related("source")
            .order_by("-date")
        )

    def get_author(self) -> Author:
        return Author.objects.get(slug=self.kwargs["slug"])

    def get_tags(self, articles) -> List[Tag]:
        return shuffle(Tag.objects.for_articles(articles).weighted())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = self.get_tags(context["object_list"])
        return context

    def get(self, request, *args, **kwargs):
        try:
            author = self.get_author()
        except Author.DoesNotExist:
            messages.warning(request, _("An author with this name could not be found"))
            return redirect(reverse("authors"))
        self.object_list = self.get_queryset()
        context = self.get_context_data(author=author)
        return self.render_to_response(context)
