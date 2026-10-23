"""dict.cc client library.

Side-effect-free API for querying dict.cc. The CLI lives in `dictcc.cli`
and is not imported here, so `import dictcc` is safe for library use.
"""

from .lib import (
    ALL_LANGS,
    PRIMARY_LANGS,
    SECONDARY_LANGS,
    USER_AGENT,
    DictCCError,
    Translation,
    make_session,
    parse_response,
    parse_suggestions,
    suggestions,
    translate,
)

__all__ = [
    "ALL_LANGS",
    "PRIMARY_LANGS",
    "SECONDARY_LANGS",
    "USER_AGENT",
    "DictCCError",
    "Translation",
    "make_session",
    "parse_response",
    "parse_suggestions",
    "suggestions",
    "translate",
]

__version__ = "0.3.0"
