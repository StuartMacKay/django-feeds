from django.db import models
from django.utils.translation import gettext_lazy as _

import tagulous  # type: ignore


class Category(tagulous.models.TagTreeModel):
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    class TagMeta:
        force_lowercase = True

    data = models.JSONField(
        verbose_name=_("Data"),
        help_text=_("Data describing a Category"),
        default=dict,
        blank=True,
    )
