# Project rules

## Design decisions

When making a non-obvious architectural or technical decision, add a section to `docs/design.md` explaining what was chosen, why, and what alternatives were considered and rejected.

## Secrets and environment files

Never read, display, or request access to `.env`, `.env.*`, or any file matched by `.claudeignore`.
If you need to know what variables an env file contains, read `.env.example` instead.
