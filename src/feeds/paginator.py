from datetime import timedelta
from math import ceil

from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.functional import cached_property

from text_unidecode import unidecode  # type: ignore


class DayPaginator(Paginator):
    """
    The DayPaginator is used to show a week's worth of Articles on each
    page, starting with today. In principle a page can be empty, though
    one a number of Sources are active this is unlikely.
    """

    def page(self, number):
        number = self.validate_number(number)
        top = (number - 1) * self.per_page
        bottom = top + self.per_page
        tomorrow = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow += timedelta(days=1)
        since = tomorrow - timedelta(days=bottom)
        until = tomorrow - timedelta(days=top)
        results = self.object_list.filter(date__gte=since, date__lt=until)
        return self._get_page(results, number, self)

    @cached_property
    def num_pages(self):
        if self.count == 0:
            return 0
        first = timezone.now()
        last = self.object_list.last().date
        return ceil((first - last).days / self.per_page)


class AlphabetPaginator(Paginator):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        super().__init__(object_list, per_page, orphans, allow_empty_first_page)

        # Build an index of the first page on which each letter
        # occurs. That allows a jump table to be displayed which
        # takes the reader to the page where items starting with
        # a given letter begin.

        self.index = {}

        attr_name = self.object_list.query.order_by[0]

        for idx, object in enumerate(self.object_list):
            # Only index objects if the field is not blank
            if value := str(getattr(object, attr_name)):
                # normalise accented characters
                letter = unidecode(value[0].upper())

                if letter not in self.index:
                    page_number = int(idx / self.per_page) + 1
                    self.index[letter] = page_number

                # Add the normalised letter to the object so a mini-heading
                # can be displayed using the ifchanged template tag
                object.index_letter = letter

                # Add the first index page where the letter occurs. That
                # allows a 'continued' label to display at the top of the
                # page
                object.index_page = self.index[letter]
