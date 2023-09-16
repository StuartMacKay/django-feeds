from django.test import TestCase
from django.urls import reverse


class IndexViewTests(TestCase):
    def test_view(self):
        response = self.client.get(reverse("app_index"))
        self.assertEqual(200, response.status_code)
