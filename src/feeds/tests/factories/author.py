import factory  # type: ignore
from faker import Faker

from feeds.models import Author

fake = Faker()


class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Author
        django_get_or_create = ("slug",)

    # Although there is a many-to-many relationship between Article
    # and Author we don't create a post_generation hook for authors
    # since that adds extra code for no added value. It's better to
    # have a single 'entry-point' for generating Articles and pass
    # an Author object as an argument if we want to generate a list
    # of Articles for a given Author.

    name = factory.Faker("name")
    slug = factory.Faker("slug")
    description = factory.Faker("html_text")
