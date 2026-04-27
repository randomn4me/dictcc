# Dictcc commandline tool

This tool enables the use of [dict.cc](https://www.dict.cc/) over the commandline.

## Installation

The project uses [uv](https://docs.astral.sh/uv/) for dependency and environment
management.

```sh
uv sync
```

## Usage

```sh
uv run dictcc Haus
uv run dictcc -p en -s fr hello world
uv run dictcc --console
```

Options:

- `-p, --prim`     primary language (default: `en`)
- `-s, --sec`      secondary language (default: `de`)
- `-m, --max`      maximum number of results to show (default: `10`)
- `-c, --console`  start an interactive console (use `q`, Ctrl-D or Ctrl-C to exit)

Run `uv run dictcc --help` for the full list.

## Requirements

Dependencies are declared in `pyproject.toml`
([requests](https://pypi.org/project/requests/),
[tabulate](https://pypi.org/project/tabulate/),
[BeautifulSoup](https://pypi.org/project/beautifulsoup4/)).
