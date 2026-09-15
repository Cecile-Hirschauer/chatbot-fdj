# fix

Auto-fix all ruff linting and formatting issues, then report what changed.

```bash
uv run ruff check . --fix && uv run ruff format .
```

After fixing, run `uv run pytest` to verify nothing is broken.
