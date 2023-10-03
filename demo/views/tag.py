from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import generic

from feeds.models import Article, Tag


class TagView(generic.ListView):
    template_name = "demo/tag.html"
    paginate_by = 20

    def get_queryset(self):
        return (
            Article.objects.published()
            .by_tag(self.kwargs["slug"])
            .filter(self.get_filters())
            .select_related("source")
            .prefetch_related("authors")
            .order_by("-date")
        )

    def get_filters(self):
        filters = Q()
        if author := self.kwargs.get("author", ""):  # noqa
            filters &= Q(authors__slug=author.strip())
        if source := self.kwargs.get("source", ""):  # noqa
            filters &= Q(source__slug=source.strip())
        return filters

    def get_tag(self):
        return Tag.objects.get(slug=self.kwargs["slug"])

    def get(self, request, *args, **kwargs):
        try:
            tag = self.get_tag()
        except Tag.DoesNotExist:
            messages.warning(request, _("A tag with this title could not be found"))
            return redirect(reverse("tags"))
        self.object_list = self.get_queryset()
        context = self.get_context_data(tag=tag)
        return self.render_to_response(context)
