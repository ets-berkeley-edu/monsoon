# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Monsoon is a from-scratch reimplementation of
[cspace-webapps-common](https://github.com/ets-berkeley-edu/cspace-webapps-common), the
multi-tenant Django framework that powers UC Berkeley's CollectionSpace (CSpace) museum web
apps (bampfa, botgarden, cinefiles, pahma, ucjeps). The stack is being rebuilt as Flask +
Vue.js, single codebase / single deployment serving all tenants (replacing the old model of a
separate physical Django project per tenant).

There is intentionally **no CalNet integration and no `authorized_users` table**. Monsoon will
pass credentials through to CollectionSpace itself rather than handling
authentication/authorization independently — don't add a local auth/session-user model without
checking this against the actual plan first.

Much of this codebase's conventions (app factory, config layering, error handling, the
SQLAlchemy/`std_commit` pattern, no-Alembic schema approach) are deliberately modeled on the
sibling project `ripley` (Flask + Vue app for UC Berkeley's Canvas LMS instance, typically
checked out at `~/git/ripley`) rather than invented fresh — when extending something and the
intent isn't obvious from this repo alone, that sibling repo is the reference implementation to
check first.

## Commands

### Setup
```bash
pip3 install -r requirements.txt
nvm use && npm install

# Postgres (one-time, local dev)
createuser monsoon --no-createdb --no-superuser --no-createrole --pwprompt
createdb monsoon --owner=monsoon
createdb monsoon_test --owner=monsoon
export FLASK_APP=application.py
flask initdb   # loads scripts/db/schema.sql and seeds the five tenants
```

### Run
```bash
python3 application.py    # Flask, port 5000
npm run serve-vue         # Vite dev server, port 8080
```
Visit `http://<tenant-slug>.localhost:8080` (e.g. `pahma.localhost:8080`) to exercise a
specific tenant locally, or plain `localhost:8080` for no tenant. See the "Multi-tenancy"
section below and the README's "Working with tenants locally" section.

### Test
```bash
tox -e test                                                    # full backend suite
pytest tests                                                    # equivalent, direct
pytest tests/test_models/test_tenant.py::TestTenant::test_get_all   # a single test
```
There is no frontend test runner configured yet — `npm run lint-vue` is the only frontend
check.

### Lint
```bash
tox -e lint-py                  # ruff, backend
ruff check --fix <path>         # ruff, with autofix
tox -e lint-vue                 # eslint, frontend
npm run lint-vue-fix            # eslint, with autofix
```

### Everything (matches `.travis.yml`)
```bash
tox -p                          # lint-py, lint-vue, build-vue, test, in parallel
```

## Architecture

### Backend/frontend split, one deployment
`monsoon/` (Flask app factory), `config/`, `scripts/db/`, and `tests/` are the backend; `src/`
is the Vue 3 + Vuetify + Pinia frontend, built by Vite. In production there is one process:
Flask serves the built bundle (`dist/static/index.html`, via `INDEX_HTML` config) for any
non-`/api` route. In development, Flask instead 302-redirects non-API routes to the Vite dev
server on `VUE_LOCALHOST_PORT`, reusing the incoming request's own hostname (not a hardcoded
`localhost`) so a tenant subdomain survives the redirect — see `front_end_route` in
`monsoon/routes.py`.

### App factory and config loading
`monsoon/factory.py:create_app()` is the single entry point (used by `application.py`,
`consoler.py`, and `tests/conftest.py`). Config loads in layers via
`monsoon/configs.py:load_configs()`: `config/default.py` → `config/{MONSOON_ENV}.py`
(`development`/`test`; env defaults to `development`) → an optional
`{MONSOON_LOCAL_CONFIGS}/{env}-local.py` file outside version control for secrets/overrides
(defaults to `../config` if `MONSOON_LOCAL_CONFIGS` isn't set). There is no `production.py` —
a real deployment is expected to override `config/default.py` entirely via that local-config
mechanism (`SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, etc.).

Routes are registered in `monsoon/routes.py:register_routes()`, called once inside an app
context in the factory. API error handling is a small typed-exception hierarchy
(`monsoon/api/errors.py`: `BadRequestError`/`UnauthorizedRequestError`/`ForbiddenRequestError`/
`ResourceNotFoundError`/`InternalServerError`, each `JsonableError` subclasses render via
`to_json()`) wired to Flask error handlers in `monsoon/api/error_handlers.py`. New API
blueprints/controllers get imported inside `register_routes()` (not at module top level) so
`@app.route` decorators run inside an active app context — follow that pattern for new
controllers under `monsoon/api/`.

### Multi-tenancy (subdomain-based)
Which museum a request is for is resolved from the subdomain of the `Host` header, not a path
or query param — e.g. `pahma.webapps.cspace.berkeley.edu` in production,
`pahma.localhost:8080` in dev (chosen over `lvh.me`-style services specifically so local dev
needs no external DNS dependency; RFC 6761 guarantees `localhost` subdomains resolve to
loopback). The pieces:

- `monsoon/lib/tenants.py:resolve_tenant_slug(host, base_domain)` — pure function, strips a
  configured `base_domain` suffix off the `Host` header to get a slug, or returns `None` (not
  an error) for a bare apex-domain request. The *same* function runs in every environment; only
  `TENANT_BASE_DOMAIN` differs per `config/*.py` file (prod domain / `localhost` / a fixture
  domain in tests).
- `monsoon/routes.py`'s `before_request` hook sets `g.tenant_slug` from that function, then
  `_reject_unrecognized_tenant()` 404s any request whose slug doesn't match a row in the
  `tenants` table — but does *not* reject a request with no subdomain at all (that's a
  separate, valid "no tenant" case). Don't conflate the two when touching this logic.
- The `tenants` table (`monsoon/models/tenant.py`) is the single source of truth for which
  slugs are valid, seeded identically (five real museums: bampfa, botgarden, cinefiles, pahma,
  ucjeps) in every environment via three independent mechanisms that should be kept in sync by
  hand: `scripts/db/migrate/2026/20260924-MON-6/create_tenants_table.sql` (production, applied
  by hand via `psql`), `tests/fixtures/tenants.sql` (loaded by the test suite), and
  `monsoon/models/development_db.py` (ORM-based, run locally via `flask initdb`).
- `/api/config` (`monsoon/api/config_controller.py`) exposes the resolved `tenantSlug`
  alongside static app config; the frontend reads it via Pinia (`src/stores/context.ts`).

### Database: no migration framework
No Alembic/Flask-Migrate, matching `ripley`. `scripts/db/schema.sql` (+ mirror-image
`drop_schema.sql`) is the canonical, cumulative DDL for a fresh database — run wholesale by
`flask initdb` and the pytest `db` fixture. Changes to an already-deployed database instead go
through a new dated, ticket-numbered file under `scripts/db/migrate/<year>/<date-ticket>/`,
applied to production by hand (`psql`) — there is no automated runner for that directory.
When a model's schema changes, update `schema.sql` *and* add a migrate file; don't rely on one
without the other.

SQLAlchemy wiring lives in `monsoon/__init__.py`: `db = SQLAlchemy()` at module scope, plus
`std_commit(allow_test_environment=False)` — the app-wide way to end a unit of work. Under
`TESTING`, it flushes instead of committing (each test runs inside one outer transaction that
`tests/conftest.py`'s per-test `db_session` fixture rolls back afterward for isolation); pass
`allow_test_environment=True` for something that must durably commit even during test setup
(schema/fixture loading does this). Models extend `monsoon/models/base.py:Base` for
`created_at`/`updated_at`, define their own primary key, and expose a `to_api_json()` plus
classmethod-style CRUD (`create`, `find_by_*`, `get_all`) — see `monsoon/models/tenant.py`.

### Frontend
Vue 3 (Composition API, `<script setup>`) + Vuetify 3 + Pinia + Vite, TypeScript throughout.
`src/main.ts` fetches `/api/config` before mounting the app and before installing the router,
so the first render already has config (including `tenantSlug`) available via
`useContextStore()` (`src/stores/context.ts`). The API base URL is computed at runtime from
`window.location` (`src/utils.ts:apiBaseUrl()`), not read as a fixed `.env` value — this is
what keeps API calls on the same tenant subdomain as the page itself in dev; don't reintroduce
a hardcoded host here. `src/router.ts` / `src/layouts/default/` / `src/views/` are still
minimal (a landing page and a catch-all 404) — no real feature routes exist yet.
