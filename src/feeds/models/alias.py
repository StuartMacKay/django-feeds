from django.db import models
from django.utils.translation import gettext_lazy as _

from django_extensions.db.models import TimeStampedModel


class Alias(TimeStampedModel):
    class Meta:
        verbose_name = _("Alias")
        verbose_name_plural = _("Aliases")

    name = models.CharField(
        verbose_name=_("Name"),
        help_text=_("A name used to lookup an author from a feed entry"),
        max_length=100,
        blank=True,
    )

    author = models.ForeignKey(
        to="feeds.Author",
        related_name="aliases",
        on_delete=models.CASCADE,
        verbose_name=_("Author"),
        help_text=_("The Author that the feed entry author maps to"),
    )

    feed = models.ForeignKey(
        to="feeds.Feed",
        on_delete=models.CASCADE,
        verbose_name=_("Feed"),
        help_text=_("The feed where the alias is used"),
    )

    def __str__(self):
        return self.name
