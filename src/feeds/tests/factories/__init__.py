import factory  # type: ignore

from feeds.tests.providers import html

from .alias import AliasFactory
from .article import ArticleFactory
from .author import AuthorFactory
from .category import CategoryFactory
from .feed import FeedFactory
from .source import SourceFactory
from .tag import TagFactory
from .user import UserFactory

__all__ = [
    "AliasFactory",
    "ArticleFactory",
    "AuthorFactory",
    "CategoryFactory",
    "FeedFactory",
    "SourceFactory",
    "TagFactory",
    "UserFactory",
]

# Register the custom providers here, so they are available anywhere
# the factories are used. This could be added to the root conftest,
# but we occasionally want to be able to create instances of factories
# in the django shell, particularly for ad-hoc testing.

factory.Faker.add_provider(html.Provider)
