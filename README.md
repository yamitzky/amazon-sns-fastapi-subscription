# Amazon SNS FastAPI Subscription

A sample implementation of Amazon SNS HTTP/HTTPS endpoint using FastAPI

https://zenn.dev/yamitzky/scraps/649f03dcde989a

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) as package manager

## Commands

Installation

```
uv sync
```

Launch (dev mode)

```bash
uv run fastapi dev app
```

Launch (production mode)

```bash
uv run fastapi run app
```

Testing

```bash
uv run pytest tests
```