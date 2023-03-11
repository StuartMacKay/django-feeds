from typing import Union

from django.db.models import QuerySet
from django.template.response import TemplateResponse


def is_paginated(response: TemplateResponse, key: str = "paginator") -> bool:
    paginator = response.context[key]
    return paginator.num_pages > 1


def is_ordered(obj: Union[QuerySet, TemplateResponse], key: str = "paginator") -> bool:
    if isinstance(obj, QuerySet):  # type: ignore
        return obj.ordered
    elif isinstance(obj, TemplateResponse):
        return obj.context[key].object_list.ordered
    return False
