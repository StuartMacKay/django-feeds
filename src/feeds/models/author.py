from django.db import models
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TimeStampedModel


class AuthorQuerySet(models.QuerySet):
    def published(self) -> "AuthorQuerySet":
        return self.filter(articles__publish=True).distinct()

    def with_slug(self, slug) -> "AuthorQuerySet":
        return self.filter(slug=slug)


AuthorManager = models.Manager.from_queryset(AuthorQuerySet)  # type: ignore


class Author(TimeStampedModel):  # type: ignore
    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")

    name = models.CharField(
        verbose_name=_("Name"),
        help_text=_("The name of the author"),
        max_length=100,
    )

    slug = AutoSlugField(
        verbose_name=_("Slug"),
        help_text=_("The slug uniquely identifying the author"),
        populate_from="name",
        max_length=100,
        unique=True,
    )

    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("A short profile of the author"),
        blank=True,
    )

    objects = AuthorManager()  # type: ignore

    def __str__(self):
        return self.name
