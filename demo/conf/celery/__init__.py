# Import the celery object into the module root, otherwise celery won't be
# able to find it, even though it is also imported in conf/__init__.py.
from .app import app  # noqa

# Receiver for setting up logging
import demo.conf.celery.logging  # noqa isort: skip
