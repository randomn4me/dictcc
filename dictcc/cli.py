"""Command-line interface for the dictcc library."""

from __future__ import annotations

import argparse
import shutil
import sys
import textwrap
from typing import Optional, Sequence

from tabulate import tabulate

from . import __version__
from .lib import (
    ALL_LANGS,
    PRIMARY_LANGS,
    DictCCError,
    Translation,
    fetch,
    make_session,
    parse_response,
    parse_suggestions,
)


def _terminal_columns(default: int = 80) -> int:
    return shutil.get_terminal_size((default, 20)).columns


def _wrap(text: str, columns: int) -> str:
    wrap_width = max(8, (columns - 8) // 2)
    return "\n   ".join(textwrap.wrap(text, wrap_width))


def _format_table(translations: list[Translation], primary: str, secondary: str) -> str:
    columns = _terminal_columns()
    rows = [[_wrap(t.source, columns), _wrap(t.target, columns)] for t in translations]
    return tabulate(rows, [primary, secondary], tablefmt="orgtbl")


def _handle(word: str, primary: str, secondary: str, max_results: int, session) -> None:
    word = word.strip()
    if not word:
        return
    try:
        html = fetch(word, primary, secondary, session=session)
    except DictCCError as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    translations = parse_response(html, max_results=max_results)
    if translations:
        print(_format_table(translations, primary, secondary))
        return

    print(f"No translation found for: {word}")
    sugg = parse_suggestions(html)
    if sugg:
        print("\nHere are suggestions given by dict.cc:")
        for s in sugg:
            print(f" - {s}")


def _run_console(initial_word: str, primary: str, secondary: str, max_results: int, session) -> None:
    try:
        import readline  # noqa: F401  (enables history/arrow keys)
    except ImportError:
        pass

    print("Starting console")
    print("Enter your words for translation")
    print("Enter q for exit (or Ctrl+D / Ctrl+C)")

    if initial_word:
        _handle(initial_word, primary, secondary, max_results, session)

    while True:
        try:
            user_input = input(">> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if user_input.strip() == "q":
            return
        _handle(user_input, primary, secondary, max_results, session)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dictcc",
        description="Query dict.cc for a translation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-p", "--prim", default="en", choices=PRIMARY_LANGS,
                        help="Primary language")
    parser.add_argument("-s", "--sec", default="de", choices=ALL_LANGS,
                        help="Secondary language")
    parser.add_argument("-c", "--console", action="store_true",
                        help="Start an interactive console")
    parser.add_argument("-m", "--max", type=int, default=10,
                        help="Maximum number of results to show")
    parser.add_argument("-V", "--version", action="version",
                        version=f"%(prog)s {__version__}")
    parser.add_argument("word", nargs=argparse.REMAINDER,
                        help="Word(s) to translate")
    return parser


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.prim == args.sec:
        parser.error(f'languages must differ (got "{args.prim}" and "{args.sec}")')
    if args.max <= 0:
        parser.error("--max must be greater than 0")
    return args


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    word = " ".join(args.word).strip()
    session = make_session()

    if args.console:
        _run_console(word, args.prim, args.sec, args.max, session)
    elif word:
        _handle(word, args.prim, args.sec, args.max, session)
    else:
        build_parser().print_help()


if __name__ == "__main__":
    main()
