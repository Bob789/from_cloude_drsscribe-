---
description: "Use when working with git, committing code, pushing to GitHub, or reviewing what should/shouldn't be tracked."
---
# Git Workflow

## Gitignore Coverage
These are protected and will NOT be pushed to GitHub:
- `.env` and all variants (`.env.local`, `.env.dev`, etc.)
- `client_secret.json` (any path)
- `private/` directory (deployment secrets)
- `docs/` directory (private documentation)
- `backend/_archive/` (deprecated code)
- `CLAUDE.md`, `.claude/` (AI agent config)
- SSL certificates (`*.pem`, `*.key`, `*.crt`)
- GCP service account keys (`*-sa.json`, `*credentials*.json`)
- Terraform state (`*.tfstate`, `*.tfvars`)

## What SHOULD be committed
- `pubspec.lock` — pinned Flutter dependency versions (DO NOT add `*.lock` to gitignore)
- `requirements.txt` — backend dependencies
- `docker-compose.yml` — infrastructure config (no secrets, uses env vars)
- `.env.example` — template showing required variables (no actual values)

## Before Pushing
1. Run `git status` and verify no sensitive files are staged
2. Check that `.env` is NOT in the list
3. Check that no `*.pem`, `*.key`, or `client_secret*.json` files are staged
