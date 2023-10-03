from django.utils.translation import gettext_lazy as _

import tagulous  # type: ignore


class Category(tagulous.models.TagTreeModel):
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    class TagMeta:
        force_lowercase = True
