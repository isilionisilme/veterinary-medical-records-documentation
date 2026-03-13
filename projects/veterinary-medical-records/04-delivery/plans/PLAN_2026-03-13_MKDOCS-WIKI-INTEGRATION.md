---
title: "Plan — MkDocs Wiki Integration"
type: plan
status: draft
created: 2026-03-13
audience: evaluator, developer
---

# Plan — MkDocs Wiki Integration

**Goal:** Publish the documentation repository as a navigable wiki-style site using MkDocs Material, served alongside the application via Docker Compose, and linked from the frontend.

**Timeframe:** ~1-2 hours (prueba técnica scope).

---

## Architecture

```
┌─────────────────────────────────────┐
│         docker compose up           │
│                                     │
│  ┌───────────┐    ┌──────────────┐  │
│  │  app       │    │  docs        │  │
│  │  :3000     │    │  :8000       │  │
│  │  (frontend │    │  (mkdocs     │  │
│  │   + API)   │    │   serve)     │  │
│  └─────┬─────┘    └──────┬───────┘  │
│        │                 │          │
│   Link: "Docs" ────────►│          │
│                                     │
└─────────────────────────────────────┘
```

- **App container:** the existing application (frontend + backend).
- **Docs container:** `mkdocs serve` on port 8000, hot-reload on file changes.
- **Link from app:** a "Documentation" button/link in the frontend pointing to `http://localhost:8000`.

---

## Steps

### Step 1 — MkDocs configuration (`mkdocs.yml`)

Create `mkdocs.yml` at the repo root with:

- **Theme:** Material for MkDocs (sidebar, search, responsive).
- **Nav:** explicit navigation tree matching the current folder structure.
- **docs_dir:** `.` (current root, since the Markdown lives at repo root).

```yaml
site_name: "Veterinary Medical Records — Documentation Wiki"
site_description: "Technical documentation for the Veterinary Medical Records system"
docs_dir: "."
site_dir: "_site"

theme:
  name: material
  palette:
    scheme: default
    primary: teal
    accent: teal
  features:
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - toc.integrate

plugins:
  - search

nav:
  - Home: README.md

  - Shared:
      - Brand Guidelines: shared/01-product/brand-guidelines.md
      - UX Guidelines: shared/01-product/ux-guidelines.md
      - Coding Standards: shared/02-tech/coding-standards.md
      - Documentation Guidelines: shared/02-tech/documentation-guidelines.md
      - LLM Benchmarks: shared/02-tech/llm-benchmarks.md
      - Way of Working: shared/03-ops/way-of-working.md

  - "Product":
      - Product Design: projects/veterinary-medical-records/01-product/product-design.md
      - UX Design: projects/veterinary-medical-records/01-product/ux-design.md
      - Design System: projects/veterinary-medical-records/01-product/design-system.md

  - "Technical":
      - Architecture: projects/veterinary-medical-records/02-tech/architecture.md
      - Technical Design: projects/veterinary-medical-records/02-tech/technical-design.md
      - Backend Implementation: projects/veterinary-medical-records/02-tech/backend-implementation.md
      - Frontend Implementation: projects/veterinary-medical-records/02-tech/frontend-implementation.md
      - Event Architecture: projects/veterinary-medical-records/02-tech/event-architecture.md
      - Extraction Quality: projects/veterinary-medical-records/02-tech/extraction-quality.md
      - Deployment: projects/veterinary-medical-records/02-tech/deployment.md
      - ADRs:
          - Index: projects/veterinary-medical-records/02-tech/adr/index.md
          - "ADR-0001 Modular Monolith": projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0001-modular-monolith.md
          - "ADR-0002 SQLite Database": projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0002-sqlite-database.md
          - "ADR-0003 Raw SQL Repository": projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0003-raw-sql-repository-pattern.md
          - "ADR-0004 In-Process Async": projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0004-in-process-async-processing.md
          - "ADR-0005 Complexity Gates": projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0005-complexity-gate-thresholds.md
          - "ADR-0006 Frontend Stack": projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0006-frontend-stack-react-tanstack-query-vite.md
          - "ADR-0007 Re-Accretion Prevention": projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0007-re-accretion-prevention-governance.md
          - "ADR-0008 Confidence Scoring": projects/veterinary-medical-records/02-tech/adr/ADR-ARCH-0008-confidence-scoring-algorithm.md

  - "Operations":
      - Architecture Audit Process: projects/veterinary-medical-records/03-ops/architecture-audit-process.md
      - Execution Rules: projects/veterinary-medical-records/03-ops/execution-rules.md
      - QA Regression Checklist: projects/veterinary-medical-records/03-ops/manual-qa-regression-checklist.md
      - Plan Creation: projects/veterinary-medical-records/03-ops/plan-creation.md
      - E2E Test Coverage: projects/veterinary-medical-records/03-ops/plan-e2e-test-coverage.md
      - Plan Execution Protocol: projects/veterinary-medical-records/03-ops/plan-execution-protocol.md

  - "Delivery":
      - Delivery Summary: projects/veterinary-medical-records/04-delivery/delivery-summary.md
      - Implementation Plan: projects/veterinary-medical-records/04-delivery/implementation-plan.md
      - Implementation History: projects/veterinary-medical-records/04-delivery/implementation-history.md
      - Future Improvements: projects/veterinary-medical-records/04-delivery/future-improvements.md

  - "Archive":
      - 12-Factor Audit: projects/veterinary-medical-records/99-archive/12-factor-audit.md
      - Codebase Audit: projects/veterinary-medical-records/99-archive/codebase-audit.md
      - CTO Review Verdict: projects/veterinary-medical-records/99-archive/cto-review-verdict.md
```

> **Note:** Backlog and Plans are excluded from the nav to keep it focused.
> They can be added later as expandable sections if desired.

### Step 2 — Dockerfile for docs service

Create `Dockerfile.docs` at the repo root:

```dockerfile
FROM python:3.12-slim

RUN pip install --no-cache-dir mkdocs-material==9.*

WORKDIR /docs
COPY . .

EXPOSE 8000

CMD ["mkdocs", "serve", "--dev-addr", "0.0.0.0:8000"]
```

- Lightweight image (~150 MB).
- Hot-reload: `mkdocs serve` watches for file changes automatically.
- No build step needed for local development.

### Step 3 — Docker Compose service

Create or extend `docker-compose.yml` (or `docker-compose.docs.yml` if app has its own):

```yaml
services:
  docs:
    build:
      context: .
      dockerfile: Dockerfile.docs
    ports:
      - "8000:8000"
    volumes:
      - .:/docs
    restart: unless-stopped
```

With the volume mount, edits to any `.md` file in the repo are reflected immediately in the browser (hot-reload).

If the app repo has its own `docker-compose.yml`, add the docs service there referencing this repo's path:

```yaml
services:
  # ... existing app services ...

  docs:
    build:
      context: ../veterinary-medical-records-documentation
      dockerfile: Dockerfile.docs
    ports:
      - "8000:8000"
    volumes:
      - ../veterinary-medical-records-documentation:/docs
    restart: unless-stopped
```

### Step 4 — Link from the application frontend

Add a navigation element in the app's header/sidebar:

```tsx
<a href="http://localhost:8000" target="_blank" rel="noopener noreferrer">
  Documentation
</a>
```

For production, make this URL configurable via environment variable:

```tsx
const DOCS_URL = import.meta.env.VITE_DOCS_URL || "http://localhost:8000";
```

### Step 5 — (Optional) GitHub Pages deployment

If you want a published version beyond local Docker:

1. Add `.github/workflows/docs.yml`:

```yaml
name: Deploy Docs
on:
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install mkdocs-material
      - run: mkdocs gh-deploy --force
```

2. Enable GitHub Pages on the `gh-pages` branch in repo settings.

Result: docs published at `https://<user>.github.io/veterinary-medical-records-documentation/`.

---

## Deliverables

| # | File | Purpose |
|---|------|---------|
| 1 | `mkdocs.yml` | MkDocs configuration with full nav tree |
| 2 | `Dockerfile.docs` | Lightweight container for docs server |
| 3 | `docker-compose.yml` (or service block) | Orchestration for docs alongside app |
| 4 | Frontend link (in app repo) | Navigation entry point to docs |
| 5 | `.github/workflows/docs.yml` (optional) | CI/CD for GitHub Pages |

## Execution order

1. Create `mkdocs.yml` → verify with `mkdocs serve` locally.
2. Create `Dockerfile.docs` → verify with `docker build`.
3. Add docs service to `docker-compose.yml` → verify with `docker compose up`.
4. Add link in app frontend → verify navigation.
5. (Optional) Add GitHub Actions workflow → verify Pages deployment.

## Risks

| Risk | Mitigation |
|------|------------|
| Some `.md` files have YAML frontmatter MkDocs doesn't expect | MkDocs Material handles frontmatter gracefully; `meta` plugin can be added if needed |
| Internal links between docs use relative paths that break | Verify with `mkdocs build --strict`; fix broken links |
| Backlog folder has 70+ files, slows nav | Excluded from nav; accessible via search |
| Port 8000 conflicts with app | Change to 8001 in compose if needed |
