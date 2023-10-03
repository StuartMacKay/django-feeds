import pytest


# Override the local setting used for development to ensure that feeds
# are always loaded by default, regardless of the time that tests are
# run. This reduces the amount of setup needed for feed-related tests.
@pytest.fixture(autouse=True)
def use_flexible_load_schedule(settings):
    settings.FEEDS_LOAD_SCHEDULE = "* * * * *"


@pytest.fixture(autouse=True)
def use_dummy_cache_backend(settings):
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
