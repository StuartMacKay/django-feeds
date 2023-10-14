# Load Open Graph Tags

Aggregating RSS feeds from different sources and presenting them in list is 
practical and convenient, but visually unappealing. The [Open Graph](https://ogp.me/)
protocol is widely supported and allows you to spice up your site by displaying 
thumbnail images for each Article. This HowTo takes you through the code needed 
to add Open Graph data to each of the Articles loaded from a Feed. 

The Open Graph data will contain the URL of the image for the Article or Source.
There are many solutions for handling images on Django sites so we will chicken
out here and leave that as an exercise for the reader, sorry.

## Load tags for each new Article

The follow code snippets add the functions needed to parse the tags from the 
web page for the Article and adds a celery task to load the data in the background
when a new Article is loaded from a Feed.

```python
# opengraph.py
from html import unescape
from typing import Dict, Union, Optional

import requests
from bs4 import BeautifulSoup  # type: ignore

from feeds.models import Article, Source
from feeds.loader import get_user_agent


def fetch_page(url):
    headers = {"User-Agent": get_user_agent()}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def parse_page(url):
    return BeautifulSoup(fetch_page(url), "lxml")


def get_headers(page):
    return page.find("head")


def get_tags(node, prefix: str) -> Dict[str, str]:
    results: Dict[str, str] = {}
    for tag in node.find_all("meta"):
        property: str = tag.get("property", "")  # noqa
        if property.startswith(prefix):
            results[property] = unescape(tag.get("content", ""))
    return results


def get_open_graph_tags(node) -> Dict[str, str]:
    tags = get_tags(node, "og:")
    tags.update(get_tags(node, "twitter:"))
    return tags


def load_tags(obj: Union[Source, Article]) -> Optional[bool]:
    """
    Load Open Graph tags for an Article or Source.
    
    Returns:
        True, if the tags were loaded,
        False, if no tags were available,
        None, if there was an error.
        
    """
    try:
        page = parse_page(obj.url)
        headers = get_headers(page)
        tags = get_open_graph_tags(headers)
        has_tags = bool(tags)
        obj.data.update(tags)
        obj.data["open_graph"] = has_tags
        obj.save()
        return has_tags
    except Exception:  # noqa
        obj.data["open_graph"] = False
        obj.save()
```

Create a Celery task to load the Open Graph data in the background.

```python
# tasks.py

from opengraph import load_tags

from feeds.models import Article
from demo.celery import app

@app.task
def load_open_graph_tags(pk: str) -> None:
    load_tags(Article.objects.get(pk=pk))

```

Now connect the Celery task to the `post_save` signal, when an Article is 
created:

```python
# receivers.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from tasks import load_open_graph_tags
from feeds.models import Article


@receiver(post_save, sender=Article, dispatch_uid="article_saved")
def article_saved(sender, instance, created, **kwargs):
    if created:
        load_open_graph_tags.delay(instance.pk)
```

The easiest place to register the receiver is in the AppConfig for your site/app:

```python
from django.apps import AppConfig


class Config(AppConfig):
    name = "myapp"

    def ready(self):
        import receivers  # noqa

```

If the data fails to load or is not yet available you could add another Celery
task to try and update it. For older Articles that might not be too important
so an alternative solution would be to load the tags manually using an action
in the Django Admin for Article. The next section shows you how to do that for
Sources and is easily copied to the ArticleAdmin.

## Load tags for each Source

Open Graph data is available for blog posts and web sites. If the data for a
Source is available then a default thumbnail can be display for Articles where
the data is not available.

The easiest way to add Open Graph data to a Source is by adding an action to 
the Django Admin for the model. Make the following changes to the ModelAdmin
for Source:

1. Add an `action` so the Open Graph Data can be loaded for Sources selected from the change list.
2. Add an attribute to `list_display` so we can easily see which Source have Open Graph data.

```python
# demo/admin/source.py

from typing import Optional
from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from opengraph import load_tags

from feeds.models import Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):

    list_display = (
        "has_open_graph_tags",
    )

    actions = ["load_opengraph_tags"]

    
    @admin.display(boolean=True, description=_("Open Graph"))
    def has_open_graph_tags(self, obj):
        return obj.data.get("open_graph", False)
    

    @admin.action(description=_("Load Open Graph data for selected Sources"))
    def load_opengraph_tags(modeladmin, request, queryset):
        for source in queryset:
            has_tags = load_tags(source)
            if has_tags is True:
                message = _("Open Graph tags for '%(name)s' were loaded successfully" % {"name": source.name}),
                messages.info(request, message)
            elif has_tags is False:
                message = _("Open Graph tags were not available for '%(name)s'" % {"name": source.name}),
                messages.warning(request, message)
            else:    
                message = _("Open Graph tags could not be loaded for '%(name)s'" % {"name": source.name}),
                messages.error(request, message)
```
