#!/usr/bin/env python3

import argparse
import shutil
import sys
import textwrap

import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
)

PRIMARY_LANGS = ["de", "en"]
SECONDARY_LANGS = [
    "bg", "bs", "cs", "da", "el", "eo", "es", "fi", "fr", "hr",
    "hu", "is", "it", "la", "nl", "no", "pl", "pt", "ro", "ru",
    "sk", "sq", "sr", "sv", "tr",
]
ALL_LANGS = PRIMARY_LANGS + SECONDARY_LANGS

session = requests.Session()
session.headers.update({"user-agent": USER_AGENT})


def terminal_columns(default=80):
    return shutil.get_terminal_size((default, 20)).columns


def request(word, primary, secondary):
    try:
        response = session.get(
            f"https://{primary}{secondary}.dict.cc/",
            params={"s": word},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    return response.content


def parse_single_tag(tag, columns):
    str_tag = " ".join(a_tag.text for a_tag in tag.find_all("a"))

    if tag.var:
        str_type = " ".join(var_tag.text for var_tag in tag.find_all("var"))
        str_tag = f"{str_type} {str_tag}"

    if tag.dfn:
        all_dfn = ", ".join(dfn_tag.text for dfn_tag in tag.find_all("dfn"))
        str_tag = f"{str_tag} ({all_dfn})"

    wrap_width = max(8, (columns - 8) // 2)
    return "\n   ".join(textwrap.wrap(str_tag, wrap_width))


def parse_response(html, max_results):
    soup = BeautifulSoup(html, "html.parser")
    data = soup.find_all("td", "td7nl")
    pairs = min(max_results, len(data) // 2)
    columns = terminal_columns()

    raw_pairs = zip(data[: pairs * 2 : 2], data[1 : pairs * 2 : 2])
    return [[parse_single_tag(f, columns), parse_single_tag(t, columns)] for f, t in raw_pairs]


def parse_suggestions(html):
    soup = BeautifulSoup(html, "html.parser")
    return [tag.a.text for tag in soup.find_all("td", "td3nl") if tag.a]


def handle_translation(word, primary_lang, secondary_lang, max_results):
    word = word.strip()
    if not word:
        return

    html = request(word, primary_lang, secondary_lang)
    data = parse_response(html, max_results)

    if data:
        print(tabulate(data, [primary_lang, secondary_lang], tablefmt="orgtbl"))
    else:
        print(f"No translation found for: {word}")
        suggestions = parse_suggestions(html)
        if suggestions:
            print("\nHere are suggestions given by dict.cc:")
            for s in suggestions:
                print(f" - {s}")


def run_console(initial_word, primary, secondary, max_results):
    try:
        import readline  # noqa: F401  (enables history/arrow keys)
    except ImportError:
        pass

    print("Starting console")
    print("Enter your words for translation")
    print("Enter q for exit (or Ctrl+D / Ctrl+C)")

    if initial_word:
        handle_translation(initial_word, primary, secondary, max_results)

    while True:
        try:
            user_input = input(">> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if user_input.strip() == "q":
            return

        handle_translation(user_input, primary, secondary, max_results)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
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
    parser.add_argument("word", nargs=argparse.REMAINDER,
                        help="Word(s) to translate")

    args = parser.parse_args(argv)

    if args.prim == args.sec:
        parser.error(f'languages must differ (got "{args.prim}" and "{args.sec}")')
    if args.max <= 0:
        parser.error("--max must be greater than 0")

    return args


def cli(argv=None):
    args = parse_args(argv)
    word = " ".join(args.word).strip()

    if args.console:
        run_console(word, args.prim, args.sec, args.max)
    elif word:
        handle_translation(word, args.prim, args.sec, args.max)
    else:
        parse_args(["--help"])


if __name__ == "__main__":
    cli()
