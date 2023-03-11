import logging
from html import unescape
from typing import Dict, Optional, Union

import requests
from bs4 import BeautifulSoup  # type: ignore

from feeds.models import Article, Source
from feeds.services.feeds import get_user_agent

log = logging.getLogger(f"{__name__}.load_tags")


def fetch_page(url):
    headers = {"User-Agent": get_user_agent()}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def parse_page(url):
    return BeautifulSoup(fetch_page(url), "lxml")


def get_head(page):
    return page.find("head")


def get_tags(node, prefix: str) -> Dict[str, str]:
    results: Dict[str, str] = {}
    for tag in node.find_all("meta"):
        property: str = tag.get("property", "")  # noqa
        if property.startswith(prefix):
            results[property] = unescape(tag.get("content", ""))
    return results


def load_tags(obj: Union[Source, Article]) -> Optional[int]:
    try:
        log.debug("Open Graph tags request", extra={"article": obj.pk, "url": obj.url})
        page = parse_page(obj.url)
        head = get_head(page)
        open_graph_tags = get_tags(head, "og:")
        twitter_tags = get_tags(head, "twitter:")
        count = len(open_graph_tags) + len(twitter_tags)
        obj.data.update(open_graph_tags)
        obj.data.update(twitter_tags)
        obj.save()
        if count:
            log.debug(
                "Open Graph tags loaded", extra={"article": obj.pk, "url": obj.url}
            )
        else:
            log.debug(
                "Open Graph tags not found", extra={"article": obj.pk, "url": obj.url}
            )
    except Exception:  # noqa
        log.exception(
            "Open Graph tags not loaded", extra={"article": obj.pk, "url": obj.url}
        )
        count = None
    return count
