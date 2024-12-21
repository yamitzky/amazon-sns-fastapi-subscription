# Amazon SNS FastAPI Subscription

Amazon SNS の HTTP/HTTPS エンドポイントを FastAPI で実装するサンプル

https://zenn.dev/yamitzky/scraps/649f03dcde989a

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) as package manager

## Commands

インストール

```
uv sync
```

起動 (dev mode)

```bash
uv run fastapi dev app
```

起動 (production mode)

```bash
uv run fastapi run app
```

テスト

```bash
uv run pytest tests
```
