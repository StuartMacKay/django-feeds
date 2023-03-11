from django.template import Template
from django.template.base import TextNode
from django.template.loader import get_template
from django.utils.html import strip_tags

import pytest

templates = [
    "feeds/articles.html",
    "feeds/author.html",
    "feeds/authors.html",
    "feeds/source.html",
    "feeds/sources.html",
    "feeds/tag.html",
    "feeds/tags.html",
]

exclude = ["-", ",", ":", "&nbsp;", ".", ";", "#", ": #", ")", "("]


@pytest.mark.parametrize("path", templates)
def test_translations(path):
    template = get_template(path)
    tagless = strip_tags(template.template.source)
    nodes = Template(tagless).nodelist.get_nodes_by_type(TextNode)
    texts = [str(node.render({})).strip() for node in nodes]
    untranslated = [text for text in texts if text and text not in exclude]
    assert len(untranslated) == 0
