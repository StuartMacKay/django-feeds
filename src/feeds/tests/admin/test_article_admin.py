from django.test import TestCase

import pytest

from feeds.tests.factories import ArticleFactory
from feeds.tests.mixins import AdminTests


# @pytest.mark.django_db
# class ArticleAdminTests(AdminTests, TestCase):
#     factory_class = ArticleFactory
#     query_count = 9
