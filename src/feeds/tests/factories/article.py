import random

from django.utils import timezone

import factory  # type: ignore
from faker import Faker

from feeds.models import Article

fake = Faker()

tzinfo = timezone.get_default_timezone()

# The distributions are used to set the probability that an Article will have
# a given number of tags, authors or clicks.

tag_distribution = [0] * 10 + [1] * 70 + [2] * 10 + [3] * 10
category_distribution = [0] * 70 + [1] * 20 + [2] * 10
author_distribution = [0] * 5 + [1] * 80 + [2] * 10 + [3] * 5
click_distribution = [0] * 5 + [1] * 80 + [2] * 10 + [3] * 5


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article

    # When articles are generated from the entries are loaded from a feed
    # any trailing period is removed so all the titles across all the feeds
    # are displayed consistently. Here we leave the trailing period in place
    # since we don't specifically test for its presence, and it keeps the
    # code simple.
    #
    # http_status is a custom provider which returns a status of 200 OK 95%
    # of the time and 404 Not Found for the remaining 5%, which is much
    # larger than the observed rate in production. The status code is not
    # used to filter Articles (just yet) but we want to create a data set
    # that is close to reality.
    #
    # The publication date is set for a random time in the past two weeks
    # since the home page is paginated by week and this will generate a
    # set of Articles across multiple pages.
    #
    # The 'publish' flag is set to True 80% of the time so the list of
    # articles in any given week contains a mix of published and unpublished
    # items.
    #
    # The post_generation hooks for tags and authors use in order
    # of precedence:
    #
    #   1. Any objects passed as arguments to the factory.
    #   2. Any existing objects from the database.
    #   3. New instances.
    #
    # The number of objects depends on the probability distributions defined
    # above.

    title = factory.Faker("sentence")
    url = factory.Faker("url")
    date = factory.Faker("date_time_between", start_date="-2w", tzinfo=tzinfo)
    summary = factory.Faker("paragraph")
    publish = factory.Faker("boolean", chance_of_getting_true=95)
    source = factory.SubFactory("feeds.tests.factories.SourceFactory")
    identifier = factory.Faker("url")
    feed = factory.SubFactory("feeds.tests.factories.FeedFactory")
    data = {"default": "value"}  # type: ignore
    views = factory.Faker('pyint', min_value=0, max_value=100)

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

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if create:
            if extracted:
                self.tags.set(extracted)
            else:
                from .tag import Tag, TagFactory

                count = random.choice(tag_distribution)

                if Tag.objects.exists():
                    tags = list(Tag.objects.all())
                    for n in range(count):
                        self.tags.add(random.choice(tags))
                else:
                    for n in range(count):
                        self.tags.add(TagFactory())

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if create:
            if extracted:
                self.authors.set(extracted)
            else:
                from .author import Author, AuthorFactory

                count = random.choice(author_distribution)

                if Author.objects.exists():
                    authors = list(Author.objects.all())
                    for n in range(count):
                        self.authors.add(random.choice(authors))
                else:
                    for n in range(count):
                        self.authors.add(AuthorFactory())

    @factory.post_generation  # type: ignore
    def data(self, create, extracted, **kwargs):
        if extracted:
            self.data = extracted
        else:
            self.data = {
                "og:title": self.title,
                "og:url": self.url,
            }
        if create:
            self.save()
