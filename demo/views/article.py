from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View, generic
from django.views.decorators.csrf import csrf_exempt

from feeds.models import Article


class ArticleView(generic.RedirectView):
    # In the off chance there are Articles with duplicate codes return the
    # url for the latest once since that's the one most likely to have been
    # clicked. If no such Article exist then return None so the RedirectView
    # responds with 410 Gone.

    def get_redirect_url(self, *args, **kwargs):
        Article.objects.viewed(kwargs["code"])
        if article := Article.objects.with_code(kwargs["code"]):
            return article.url


@method_decorator(csrf_exempt, name="dispatch")
class ArticleClickView(View):
    # Record outbound link clicks via POST so no trail on who clicked what
    # is left in the web server logs.

    def post(self, request):
        code = request.POST.get("code")
        Article.objects.viewed(code)
        return HttpResponse(status=204)
