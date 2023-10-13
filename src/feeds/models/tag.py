from typing import Dict, List

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from django_extensions.db.models import TimeStampedModel


class TagQuerySet(models.QuerySet):
    def for_articles(self, articles) -> "TagQuerySet":
        return self.filter(article__in=articles)

    def weighted(self) -> "List[Tag]":
        results: Dict[Tag, int] = {}

        for tag in self:
            results.setdefault(tag, 0)
            results[tag] += 1

        counts = results.values()

        if counts:
            highest = max(counts)
            lowest = min(counts)
            delta = highest - lowest + 1
            categories = 6
            interval = delta / categories

            for tag, count in results.items():
                tag.weight = int((count - lowest) / interval) + 1

        return list(results.keys())


TagManager = models.Manager.from_queryset(TagQuerySet)  # type: ignore


class Tag(TimeStampedModel):  # type: ignore
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    name = models.CharField(
        verbose_name=_("Name"),
        help_text=_("The name of the tag"),
        max_length=100,
        default="",
    )

    slug = AutoSlugField(
        verbose_name=_("Slug"),
        help_text=_(
            "The slug uniquely identifying the tag. Generated automatically when field is left blank."
        ),
        populate_from="name",
        max_length=100,
        unique=True,
        editable=True,
    )

    summary = models.TextField(
        verbose_name=_("Summary"),
        help_text=_("A short summary of what the tag covers"),
        blank=True,
    )

    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("A more detailed description of the tag. May be in HTML"),
        blank=True,
    )

    related = models.ManyToManyField(
        to="self",
        verbose_name=_("Related tags"),
        help_text=_("The set of tag(s) that are related to this one"),
        blank=True,
    )

    objects = TagManager()  # type: ignore

    def __str__(self):
        return self.name
