from faker import Faker
from faker.providers import BaseProvider

fake = Faker()


class Provider(BaseProvider):
    def html_text(self):  # noqa
        return "<h1>%s</h1><p>%s</p>" % (fake.sentence(), fake.paragraph())
