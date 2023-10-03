from .alias import Alias
from .article import Article
from .author import Author
from .category import Category
from .feed import Feed
from .source import Source
from .tag import Tag

__all__ = (
    "Alias",
    "Article",
    "Author",
    "Category",
    "Feed",
    "Source",
    "Tag",
)

"""
Overview of the models

Alias is a lookup table mapping author names loaded from a feed to Author
objects. Feed from Wordpress accounts often contain the username for the
account so this table allows you map that to a real name. It also means
that we don't leak account details.

An Article is created for each entry in a Feed. Each time a Feed is loaded
new Articles are created or existing ones updated. The identifier field from
the feed is used to find the Article. When an Article is updated only the
title, url, date and summary change. The Authors and Tags are not updated.
That allows you, for example, to set the correct Author of a guest post or
add new Tags in the Django Admin without losing the changes the next time
the Feed is loaded. You can add Articles manually via the Django Admin.
That way you can pick and choose articles from sites that only occasionally
publish articles of interest.

Author is added as a separate model so we can easily identify all their posts,
particularly if they contribute articles to more than one site. The Alias
model ties a name to an Author for a given Feed. That means we can handle
multiple Authors with the same name and still keep their work separate.

Category is used to classify Articles. Categories are added from the Feed
model when an Article is created. Categories are multi-purpose. The model
uses Django-tagulous to create hierarchical tags, so for example, you can
add "media/video" to Articles created from a YouTube feed. Categories can
also be used to add meta-data to Articles, for example, "label/repost",
"label/paywalled", etc.

Feed contains the URL for an RSS/Atom feed and the schedule to which the
feed will be loaded via Celery or cron. The default schedule is to load
Feeds every hour, on the hour. However, you can also set the schedule for
individual Feeds. The Feed model also contains flags on how the feed is
loaded or processed. The 'load_tags' flag is used to control whether the
tags from each entry in the feed are added to the Article. That is useful
as some authors diligently tag their posts while others simply leave the
default 'Uncategorized' tag in place. There is also an `auto_publish'
flag which is used to set the 'publish' flag on Article. That way you
can pick and choose which Articles to publish.

A Source represents any web site that syndicates their content. The model
exists as sites can publish one or more feeds, e.g. newspapers and this
allows you to identify all the Articles published on a given site. You
could also use the Category model to identify which section the Article
was published on, e.g. "news/environment", "news/business", etc. and
organised the Articles accordingly.

A Tag is a tag added to an Article from a feed entry or via the Django
Admin. Like Author, it exists a model, rather than a comma-delimited set
of strings, so Articles from different feeds about the same subject can
be identified.

The models are intended to be flexible. The hierarchical tags supported
by tagulous can be used to add any kind of meta-data since you can easily
fetch the set of Categories for a given prefix. The Source and Article
models also have a JSON field which can be used to extend the models in
any way you choose. One example would be to add OpenGraph data for
thumbnail images to create a magazine style layout for a site.
"""
