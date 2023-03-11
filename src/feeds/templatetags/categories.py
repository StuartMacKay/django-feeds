from django import template

register = template.Library()


@register.filter
def categories(value, arg):
    """Returns all the Category objects on an Article or Feed with a given prefix.

    The set of matching Categories objects is created using a list comprehension
    as it assumes the categories were prefetched whereas filtering the QuerySet
    would trigger another fetch from the database.

    """
    return [
        category
        for category in value.categories.all()
        if category.name.startswith(arg) and category.level > 1
    ]
