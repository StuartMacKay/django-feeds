#!/usr/bin/env python
"""
setup.py

setup() is configured with the project metadata so setup.cfg is used
primarily for options for the various tools used.

"""
import os

from setuptools import setup


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as fp:
        return fp.read()


setup(
    name="django-rss-feeds",
    version="0.0.0",
    description="An aggregator for RSS and Atom feeds.",
    long_description=read("README.md"),
    long_description_content_type="text/x-rst",
    author="Stuart MacKay",
    author_email="smackay@flagstonesoftware.com",
    keywords="django, rss, atom",
    url="https://github.com/StuartMacKay/django-feeds",
    packages=["feeds", "feeds/migrations"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2,<3.3",
        "croniter",
        "django-extensions",
        "django-tagulous",
        "feedparser",
        "python-dateutil",
        "psycopg2-binary",
    ],
    license="License :: OSI Approved :: Apache Software License",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.10",
    ],
)
