import factory  # type: ignore
from faker import Faker

from feeds.models import Tag

fake = Faker()


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = ("slug",)

    name = factory.Faker("word")
    slug = factory.Faker("slug")
    summary = factory.Faker("paragraph")
    description = factory.Faker("html_text")
