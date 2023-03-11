from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View, generic
from django.views.decorators.csrf import csrf_exempt

from feeds.models import Article
from feeds.services.articles import article_clicked


class ArticleView(generic.RedirectView):
    # In the off chance there are Articles with duplicate codes return the
    # latest once since that's the one most likely to be clicked. In the
    # extremely unlikely event this occurs, so it's better to return the most
    # likely article than a not found error since the person is clicking on
    # the link in an email or on a third-party site.

    def get_redirect_url(self, *args, **kwargs):
        article = Article.objects.filter(code=kwargs["code"]).latest("created")
        article_clicked(article)
        return article.url


@method_decorator(csrf_exempt, name="dispatch")
class ArticleClickView(View):
    # Record outbound link clicks via POST so no trail on who clicked what
    # is left in the web server logs.

    def post(self, request):
        code = request.POST.get("code")
        if article := Article.objects.filter(code=code).first():
            article_clicked(article)
        return HttpResponse(status=204)
