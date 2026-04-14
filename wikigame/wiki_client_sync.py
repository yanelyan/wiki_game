from __future__ import annotations

from typing import Any

import requests
from requests import exceptions as requests_exceptions

from .utils import normalize_title

API_URL_RU = "https://ru.wikipedia.org/w/api.php"


class WikiClientSync:
    def __init__(
        self,
        *,
        user_agent: str = "WikiGameCourseBot/1.0 (edu)",
        verify_ssl: bool = True,
        ca_bundle: str | None = None,
    ):
        self.api_url = API_URL_RU
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": user_agent})
        self.cache: dict[str, list[str]] = {}
        self.backlinks_cache: dict[str, list[str]] = {}
        self._verify: bool | str = ca_bundle if ca_bundle is not None else verify_ssl
        if self._verify is False:
            _disable_insecure_warnings()

    def get_links(self, title: str, *, limit: int = 500) -> list[str]:
        title = normalize_title(title)
        if title in self.cache:
            return self.cache[title]

        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "redirects": 1,
            "titles": title,
            "prop": "links",
            "plnamespace": 0,
            "pllimit": min(limit, 500),
        }

        links: list[str] = []
        while True:
            resp = self._session.get(self.api_url, params=params, timeout=20, verify=self._verify)
            resp.raise_for_status()
            data = resp.json()

            pages = data.get("query", {}).get("pages", {})
            for _pageid, page in pages.items():
                for link in page.get("links", []):
                    link_title = link.get("title")
                    if isinstance(link_title, str):
                        links.append(link_title)

            cont = data.get("continue")
            if not cont:
                break
            params.update(cont)

        self.cache[title] = links
        return links

    def get_backlinks(self, title: str, *, limit: int = 500) -> list[str]:
        title = normalize_title(title)
        if title in self.backlinks_cache:
            return self.backlinks_cache[title]

        params: dict[str, Any] = {
            "action": "query",
            "format": "json",
            "list": "backlinks",
            "bltitle": title,
            "blnamespace": 0,
            "bllimit": min(limit, 500),
        }

        backlinks: list[str] = []
        while True:
            resp = self._session.get(self.api_url, params=params, timeout=20, verify=self._verify)
            resp.raise_for_status()
            data = resp.json()

            for page in data.get("query", {}).get("backlinks", []):
                backlink_title = page.get("title")
                if isinstance(backlink_title, str):
                    backlinks.append(backlink_title)

            cont = data.get("continue")
            if not cont:
                break
            params.update(cont)

        self.backlinks_cache[title] = backlinks
        return backlinks


def _disable_insecure_warnings() -> None:
    try:
        import urllib3
    except Exception:
        return

    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception:
        return
