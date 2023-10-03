import factory  # type: ignore
from faker import Faker

from feeds.models import Category

fake = Faker()


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker("word")
    slug = factory.Faker("slug")
