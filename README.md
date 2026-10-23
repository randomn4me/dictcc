# Dictcc commandline tool

This tool enables the use of [dict.cc](https://www.dict.cc/) over the commandline.

## Installation

The project uses [uv](https://docs.astral.sh/uv/) for dependency and environment
management.

```sh
uv sync
```

## CLI usage

```sh
uv run dictcc Haus
uv run dictcc -p en -s fr hello world
uv run dictcc --console
python -m dictcc Haus
```

Options:

- `-p, --prim`     primary language (default: `en`)
- `-s, --sec`      secondary language (default: `de`)
- `-m, --max`      maximum number of results to show (default: `10`)
- `-c, --console`  start an interactive console (use `q`, Ctrl-D or Ctrl-C to exit)

Run `uv run dictcc --help` for the full list.

## Library usage

The package is split into `dictcc` (library) and `dictcc.cli`, so you can
import it without pulling in the CLI machinery:

```python
import dictcc

for t in dictcc.translate("Haus", "de", "en", max_results=5):
    print(t.source, "->", t.target)

# No results? Ask for spelling suggestions.
print(dictcc.suggestions("Haus", "de", "en"))
```

Reuse an HTTP session across calls:

```python
import dictcc

session = dictcc.make_session()
dictcc.translate("Haus", "de", "en", session=session)
dictcc.translate("Baum", "de", "en", session=session)
```

Network failures raise `dictcc.DictCCError`; invalid language pairs raise
`ValueError`. The `Translation` dataclass has `.source` / `.target` and
unpacks like a 2-tuple.

## Requirements

Dependencies are declared in `pyproject.toml`
([requests](https://pypi.org/project/requests/),
[tabulate](https://pypi.org/project/tabulate/),
[BeautifulSoup](https://pypi.org/project/beautifulsoup4/)).
