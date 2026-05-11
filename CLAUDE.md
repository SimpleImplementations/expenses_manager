# Project rules

## Design decisions

When making a non-obvious architectural or technical decision, add a short section to `docs/design.md` (2–4 lines). Keep entries brief — only expand into multiple bullets if the decision is genuinely complex or was explicitly requested to be detailed.

## Tests

Always add unit tests for new features, endpoints, and non-trivial logic. Run `.venv/bin/pytest tests/ -v` after writing them and fix any failures before considering the task done.

## Secrets and environment files

Never read, display, or request access to `.env`, `.env.*`, or any file matched by `.claudeignore`.
If you need to know what variables an env file contains, read `.env.example` instead.
