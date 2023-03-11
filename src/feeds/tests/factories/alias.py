import factory  # type: ignore
from faker import Faker

from feeds.models import Alias

fake = Faker()


class AliasFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Alias

    name = factory.Faker("user_name")
    author = factory.SubFactory("feeds.tests.factories.AuthorFactory")
    feed = factory.SubFactory("feeds.tests.factories.FeedFactory", enabled=True)
