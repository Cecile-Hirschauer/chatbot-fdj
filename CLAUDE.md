# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Package Manager

This project uses `uv` for dependency management and packaging.

```bash
uv sync                  # Install dependencies
uv add <package>         # Add a dependency
uv add --dev <package>   # Add a dev dependency
```

## Commands

```bash
uv run streamlit run <app_file.py>   # Run the Streamlit app
uv run chatbot-fdj                   # Run via the CLI entry point
uv run pytest                        # Run all tests
uv run pytest tests/test_foo.py      # Run a single test file
uv run pytest -k "test_name"         # Run a specific test by name
```

## Code Style & Linting

- **Language**: all code, comments, docstrings, variable names, and commit messages must be in **English**
- **Linter**: `ruff` — run before every commit:

```bash
uv run ruff check .          # Check for linting issues
uv run ruff check . --fix    # Auto-fix fixable issues
uv run ruff format .         # Format code
```

Ruff is configured in `pyproject.toml` under `[tool.ruff]`. Never disable ruff rules without a justified inline comment (`# noqa: <code>`).

## Streamlit Conventions

- Each Streamlit page is a separate `.py` file under `pages/`
- Use `st.session_state` for state that must persist across reruns
- Heavy computations (data loading, API calls) must be wrapped in `@st.cache_data` or `@st.cache_resource`
- Keep UI rendering and business logic in separate functions/modules

## Architecture

This is an early-stage Streamlit chatbot application with the following structure:

- **`src/chatbot_fdj/`** - Main package (src layout)
  - `__init__.py` - Contains the `main()` entry point
- **Entry point**: `chatbot-fdj` CLI command maps to `chatbot_fdj:main`
- **Key dependencies**: `streamlit`, `pandas`, `python-dotenv`
- **Python version**: 3.13 (enforced via `.python-version`)

Environment variables should be managed via `.env` files (loaded with `python-dotenv`).
