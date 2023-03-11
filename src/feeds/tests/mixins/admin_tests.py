from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

import pytest

from feeds.tests.factories import UserFactory


@pytest.mark.django_db
class AdminTests:
    """Tests for the Django Admin

    The tests only check the changelist view, since that is where most of
    the errors will occur. There is little value in testing the add, change
    or delete views since we would just be testing Django itself. When these
    are customised or if the on_delete rules in the underlying models do not
    allow cascaded deletes, generic tests would either not work or add very
    little value.

    """

    # The FactoryBoy class for creating objects
    factory_class = None
    # The number of objects to create
    batch_size = 10

    @classmethod
    def setUpTestData(cls):
        cls.admin = UserFactory(is_staff=True, is_superuser=True)
        cls.model = cls.factory_class._meta.model  # noqa
        cls.app_label = cls.model._meta.app_label  # noqa
        cls.model_name = cls.model._meta.model_name  # noqa
        cls.objects = cls.factory_class.create_batch(cls.batch_size)

    def clear_query_caches(self):  # noqa
        ContentType.objects.clear_cache()

    def setUp(self):
        self.client.force_login(self.admin)  # noqa

    def test_changelist_view(self):
        """Verify the changelist view is displayed without any errors"""
        url = reverse("admin:%s_%s_changelist" % (self.app_label, self.model_name))
        response = self.client.get(url)  # noqa
        assert response.status_code == 200

    def test_changelist_search(self):
        """Verify search_fields does not contain any invalid lookups"""
        url = reverse("admin:%s_%s_changelist" % (self.app_label, self.model_name))
        response = self.client.get(url, {"q": "test"}, follow=True)  # noqa
        assert response.status_code == 200

    def test_changelist_query_count(self):
        """Verify the number of queries is fixed when a new object is added"""
        url = reverse("admin:%s_%s_changelist" % (self.app_label, self.model_name))

        self.clear_query_caches()
        with self.assertNumQueries(self.query_count):  # noqa
            self.client.get(url)  # noqa

        # Add another object
        self.factory_class()

        self.clear_query_caches()
        # The number of queries should remain the same
        with self.assertNumQueries(self.query_count):  # noqa
            self.client.get(url)  # noqa
