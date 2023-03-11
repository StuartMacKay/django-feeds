import datetime as dt

from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel
from tagulous.models import TagField


def article_code():
    return get_random_string(6)


class ArticleQuerySet(models.QuerySet):
    def published(self) -> "ArticleQuerySet":
        return self.filter(publish=True)

    def for_date(self, date: dt.date) -> "ArticleQuerySet":
        return self.filter(date__date=date)

    def since_date(self, date: dt.date) -> "ArticleQuerySet":
        return self.filter(date__date__gt=date)

    def by_author(self, slug) -> "ArticleQuerySet":
        return self.filter(authors__slug=slug)

    def by_source(self, slug) -> "ArticleQuerySet":
        return self.filter(source__slug=slug)

    def by_tag(self, slug) -> "ArticleQuerySet":
        return self.filter(tags__slug=slug)

    def with_code(self, code) -> "ArticleQuerySet":
        return self.filter(code=code)

    def with_identifier(self, identifier) -> "ArticleQuerySet":
        return self.filter(identifier=identifier)


ArticleManager = models.Manager.from_queryset(ArticleQuerySet)  # type: ignore


class Article(TimeStampedModel):
    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        get_latest_by = "date"

    title = models.CharField(
        verbose_name=_("Title"),
        help_text=_("The title of the article"),
        max_length=1000,
    )

    authors = models.ManyToManyField(
        to="feeds.Author",
        related_name="articles",
        verbose_name=_("Authors"),
        help_text=_("The author(s) who wrote the article"),
    )

    url = models.URLField(
        verbose_name=_("URL"),
        help_text=_("The link to the article on the source's web site"),
        max_length=2000,
    )

    code = models.CharField(
        verbose_name=_("Code"),
        help_text=_("The code that used to identify the article"),
        max_length=6,
        default=article_code,
    )

    archive_url = models.URLField(
        verbose_name=_("Archive URL"),
        help_text=_(
            "The link to the archived article using a service such as archive.today"
        ),
        max_length=2000,
        blank=True,
    )

    date = models.DateTimeField(
        verbose_name=_("Date"),
        help_text=_("The date the article was published by the source"),
    )

    summary = models.TextField(
        verbose_name=_("Summary"),
        help_text=_("A summary of the article"),
        blank=True,
    )

    source = models.ForeignKey(
        to="feeds.Source",
        related_name="articles",
        on_delete=models.CASCADE,
        verbose_name=_("Source"),
        help_text=_("The source (blog, news site, etc.) which published the article"),
    )

    feed = models.ForeignKey(
        to="feeds.Feed",
        related_name="articles",
        on_delete=models.PROTECT,
        verbose_name=_("RSS Feed"),
        help_text=_("The feed from the host web site"),
        null=True,
        blank=True,
    )

    identifier = models.CharField(
        verbose_name=_("Identifier"),
        help_text=_("The unique identifier for the Article from the Feed"),
        max_length=2000,
        blank=True,
    )

    comment = models.TextField(
        verbose_name=_("Comment"),
        help_text=_("An editorial comment about the article"),
        blank=True,
    )

    publish = models.BooleanField(
        verbose_name=_("Publish"),
        help_text=_("Publish the article on the site"),
        default=False,
        db_index=True,
    )

    categories = TagField(
        verbose_name=_("Categories"),
        help_text=_("The categories that describes the article contents"),
        to="feeds.Category",
        blank=True,
    )

    # Tags are added after the article is added to the database.
    # The idea is that articles on the same subjects from different
    # sources have the same set of Tags - more or less.

    tags = models.ManyToManyField(
        verbose_name=_("Tags"),
        help_text=_("Keywords for subjects covered in the content"),
        to="feeds.Tag",
        blank=True,
    )

    views = models.PositiveIntegerField(
        verbose_name=_("Views"),
        help_text="The number of times the article has been viewed (read)",
        default=0,
    )

    data = models.JSONField(
        verbose_name=_("Data"),
        help_text=_("Data describing an article"),
        default=dict,
        blank=True,
    )

    objects = ArticleManager()  # type: ignore

    def __str__(self) -> str:
        return self.title

    def has_authors(self):
        names = [author.name for author in self.authors.all()]
        return names and " ".join(names) != self.source.name
