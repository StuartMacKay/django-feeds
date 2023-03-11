from django.test import TestCase

import pytest

from feeds.tests.factories import AliasFactory
from feeds.tests.mixins import AdminTests


@pytest.mark.django_db
class AliasAdminTests(AdminTests, TestCase):
    factory_class = AliasFactory
    query_count = 5
