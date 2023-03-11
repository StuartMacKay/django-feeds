from django.db import models
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TimeStampedModel


class Source(TimeStampedModel):  # type: ignore
    class Meta:
        verbose_name = _("Source")
        verbose_name_plural = _("Sources")

    name = models.CharField(
        verbose_name=_("Name"),
        help_text=_("The name of the source"),
        max_length=100,
    )

    slug = AutoSlugField(
        verbose_name=_("Slug"),
        help_text=_("The slug uniquely identifying the source"),
        populate_from="name",
        max_length=100,
        db_index=True,
    )

    url = models.URLField(
        verbose_name=_("Web site"),
        help_text=_("The URL for source's web site"),
        blank=True,
    )

    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("A description of the source"),
        blank=True,
    )

    data = models.JSONField(
        verbose_name=_("Data"),
        help_text=_("Data describing a source"),
        default=dict,
        blank=True,
    )

    def __str__(self):
        return self.name
