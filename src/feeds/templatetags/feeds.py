from typing import List

from django import template

from feeds.models import Article, Category

register = template.Library()


@register.filter
def categories(article: Article, prefix: str) -> List[Category]:
    """Returns all the Category objects on an Article with a given prefix.

    The following code snippet shows how categories can be used to display
    labels, e.g. "New", "Updated", etc. which have been added to an Article:

    {% load categories %}

    {% for article in articles %}
      <li>
        <a rel="external" href="{{ article.url }}">{{ article.title }}</a>
          {% for label in article|categories:"label" %}
            <span class="label-{{ label.slug }}">{{ label.label|capfirst }}</span>
          {% endfor %}
      </l1>
    {% endfor %}

    NOTE: the label slug is used to select the CSS class for styling. It would
    be clumsy to embed the styling for each label type in the template. This
    works when the set of labels is predefined. However, in situations where
    the labels are not known in advance then it would make more sense to store
    them in a (JSON) field on the Category model.

    NOTE: the set of matching Categories objects is created using a list
    comprehension as it assumes the categories were prefetched. Using
    filter() would trigger another fetch from the database.

    """
    return [
        category
        for category in article.categories.all()
        if category.name.startswith(prefix) and category.level > 1
    ]
