import random

import factory  # type: ignore
from faker import Faker

from feeds.models import Feed

fake = Faker()


# The distributions are used to set the probability that a Feed will have
# a given number of categories.

category_distribution = [0] * 0 + [1] * 70 + [2] * 20 + [10] * 3


class FeedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Feed

    name = factory.Faker("word")
    url = factory.Faker("url")
    source = factory.SubFactory("feeds.tests.factories.SourceFactory")
    auto_publish = factory.Faker("boolean", chance_of_getting_true=90)

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if create:
            if extracted:
                self.categories.set(extracted)
            else:
                from .category import Category, CategoryFactory

                count = random.choice(category_distribution)

                if Category.objects.exists():
                    categories = list(Category.objects.all())
                    for n in range(count):
                        self.categories.add(random.choice(categories))
                else:
                    for n in range(count):
                        self.categories.add(CategoryFactory())
