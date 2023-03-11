from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from feeds.tasks import load_opengraph_tags
from feeds.models import Article


@receiver(post_save, sender=Article, dispatch_uid="article_saved")
def article_saved(sender, instance, created, **kwargs):
    if created:
        if settings.LOAD_OPEN_GRAPH_DATA:
            load_opengraph_tags.delay(instance.pk)
