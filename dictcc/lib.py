"""Core dict.cc query and parsing. No printing, no argparse."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
)

PRIMARY_LANGS: list[str] = ["de", "en"]
SECONDARY_LANGS: list[str] = [
    "bg", "bs", "cs", "da", "el", "eo", "es", "fi", "fr", "hr",
    "hu", "is", "it", "la", "nl", "no", "pl", "pt", "ro", "ru",
    "sk", "sq", "sr", "sv", "tr",
]
ALL_LANGS: list[str] = PRIMARY_LANGS + SECONDARY_LANGS


class DictCCError(RuntimeError):
    """Raised when a dict.cc request fails."""


@dataclass(frozen=True)
class Translation:
    source: str
    target: str

    def __iter__(self):
        yield self.source
        yield self.target


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"user-agent": USER_AGENT})
    return s


def _validate_langs(primary: str, secondary: str) -> None:
    if primary not in PRIMARY_LANGS:
        raise ValueError(
            f"primary language must be one of {PRIMARY_LANGS}, got {primary!r}"
        )
    if secondary not in ALL_LANGS:
        raise ValueError(
            f"secondary language must be one of {ALL_LANGS}, got {secondary!r}"
        )
    if primary == secondary:
        raise ValueError(
            f"primary and secondary languages must differ (got {primary!r} twice)"
        )


def fetch(
    word: str,
    primary: str,
    secondary: str,
    *,
    session: Optional[requests.Session] = None,
    timeout: float = 10.0,
) -> bytes:
    """Fetch the raw HTML result page from dict.cc."""
    _validate_langs(primary, secondary)
    sess = session or make_session()
    try:
        response = sess.get(
            f"https://{primary}{secondary}.dict.cc/",
            params={"s": word},
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise DictCCError(str(e)) from e
    return response.content


def _text_from_tag(tag) -> str:
    text = " ".join(a.text for a in tag.find_all("a"))
    if tag.var:
        type_str = " ".join(v.text for v in tag.find_all("var"))
        text = f"{type_str} {text}"
    if tag.dfn:
        dfns = ", ".join(d.text for d in tag.find_all("dfn"))
        text = f"{text} ({dfns})"
    return text.strip()


def parse_response(html: bytes | str, max_results: Optional[int] = None) -> list[Translation]:
    """Extract translation pairs from a dict.cc result HTML page."""
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.find_all("td", "td7nl")
    pair_count = len(cells) // 2
    if max_results is not None:
        pair_count = min(max_results, pair_count)
    sources = cells[: pair_count * 2 : 2]
    targets = cells[1 : pair_count * 2 : 2]
    return [
        Translation(_text_from_tag(s), _text_from_tag(t))
        for s, t in zip(sources, targets)
    ]


def parse_suggestions(html: bytes | str) -> list[str]:
    """Extract dict.cc's spelling / term suggestions from a result page."""
    soup = BeautifulSoup(html, "html.parser")
    return [tag.a.text for tag in soup.find_all("td", "td3nl") if tag.a]


def translate(
    word: str,
    primary: str = "en",
    secondary: str = "de",
    *,
    max_results: Optional[int] = None,
    session: Optional[requests.Session] = None,
    timeout: float = 10.0,
) -> list[Translation]:
    """Translate `word` between `primary` and `secondary`.

    Returns an empty list when dict.cc has no match; call `suggestions()`
    on the same word to retrieve spelling suggestions in that case.
    """
    html = fetch(word, primary, secondary, session=session, timeout=timeout)
    return parse_response(html, max_results=max_results)


def suggestions(
    word: str,
    primary: str = "en",
    secondary: str = "de",
    *,
    session: Optional[requests.Session] = None,
    timeout: float = 10.0,
) -> list[str]:
    """Return dict.cc's spelling / term suggestions for `word`."""
    html = fetch(word, primary, secondary, session=session, timeout=timeout)
    return parse_suggestions(html)
