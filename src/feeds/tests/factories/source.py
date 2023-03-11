import factory  # type: ignore
from faker import Faker

from feeds.models import Source

fake = Faker()


class SourceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Source
        django_get_or_create = ("slug",)

    name = factory.Faker("name")
    slug = factory.Faker("slug")
    url = factory.Faker("url")
    data = {"default": "value"}  # type: ignore

    @factory.post_generation  # type: ignore
    def data(self, create, extracted, **kwargs):
        if extracted:
            self.data = extracted
        else:
            self.data = {
                "og:title": self.name,
                "og:url": self.url,
            }
        if create:
            self.save()
