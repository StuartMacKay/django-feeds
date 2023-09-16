from django.apps import AppConfig


def setup_app_settings():
    from django.conf import settings

    from . import settings as defaults

    for name in dir(defaults):
        if name.isupper() and not hasattr(settings, name):
            setattr(settings, name, getattr(defaults, name))


class Config(AppConfig):
    name = "app_project"
    verbose_name = "App Project"

    def ready(self):
        setup_app_settings()
