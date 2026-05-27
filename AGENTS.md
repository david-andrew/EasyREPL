## Cursor Cloud specific instructions

**EasyREPL** is a small Python library (~140 lines) providing readline-based REPL interfaces. It has zero external dependencies (stdlib only).

### Development commands

| Task | Command |
|------|---------|
| Install deps | `poetry install` |
| Build | `poetry build` |
| Run echo demo | `poetry run python -m easyrepl.repl` |
| Import test | `poetry run python -c "from easyrepl import REPL, readl"` |

### Notes

- There is **no test suite** in this repository — no `tests/` directory, no pytest config.
- There is **no linter config** — no ruff/flake8/mypy setup.
- The library requires a Unix/POSIX system with GNU readline support (won't work on Windows).
- The REPL is interactive (uses `input()` and `readline`), so automated testing requires piping stdin or using a PTY. Example: `echo "hello" | poetry run python -c "from easyrepl import REPL; [print(l) for l in REPL()]"`
- Poetry creates a virtualenv in `~/.cache/pypoetry/virtualenvs/`; use `poetry run` to execute within it.
