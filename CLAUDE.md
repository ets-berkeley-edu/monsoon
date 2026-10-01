# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Monsoon is a from-scratch reimplementation of
[cspace-webapps-common](https://github.com/ets-berkeley-edu/cspace-webapps-common), the
multi-tenant Django framework that powers UC Berkeley's CollectionSpace (CSpace) museum web
apps (bampfa, cinefiles, pahma, ucbg, ucjeps -- `ucbg` is `botgarden` in the legacy
implementation; see "Multi-tenancy" below). The stack is being rebuilt as Flask +
Vue.js, single codebase / single deployment serving all tenants (replacing the old model of a
separate physical Django project per tenant).

There is intentionally **no CalNet integration and no `authorized_users` table**. A "login" is
just a CollectionSpace username/password, verified directly against the current tenant's own
CollectionSpace instance (`monsoon/externals/collectionspace.py`) — Monsoon has no independent
accounts of its own. Don't add a local auth/session-user model without checking this against
the actual plan first.

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

# Redis (one-time, local dev; optional -- tests use a fake in-memory client instead)
brew install redis && redis-server
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
  slugs are valid, seeded identically (five real museums: bampfa, cinefiles, pahma, ucbg,
  ucjeps) in every environment via three independent mechanisms that should be kept in sync by
  hand: `scripts/db/migrate/2026/` (production, applied by hand via `psql` -- `20260924-MON-6`
  creates and seeds the table), `tests/fixtures/tenants.sql`
  (loaded by the test suite), and `monsoon/models/development_db.py` (ORM-based, run locally via
  `flask initdb`). Slugs are chosen to match CollectionSpace's own tenant identifiers exactly
  (see "Authentication" below) rather than the legacy cspace-webapps-common names -- `ucbg` was
  `botgarden` there.
- `/api/config` (`monsoon/api/config_controller.py`) exposes the resolved `tenantSlug`
  alongside static app config; the frontend reads it via Pinia (`src/stores/context.ts`).

### Authentication (CollectionSpace pass-through, via Redis)
Logging in makes one real call to the current tenant's CollectionSpace instance (`GET
/accounts/0/accountperms` -- csid "0" is a deliberate CollectionSpace sentinel that always
resolves to "whichever account is currently authenticated", so a clean response is itself the
proof of a valid login). There is no independent Monsoon account. The pieces, split the same
way Ripley splits `externals/canvas.py`/`externals/mailgun.py` from its route/lib layers:

- `monsoon/externals/collectionspace.py` -- `instance_url_for_slug()` builds a tenant's
  CollectionSpace instance URL on the fly from its slug plus `COLLECTIONSPACE_BASE_DOMAIN`
  (`qa.collectionspace.org` by default -- the same tier for local dev and dev/qa deployments;
  production overrides to `collectionspace.org` via local config). Nothing is stored on the
  `tenants` table for this -- it works with no per-tenant exceptions because our tenant slugs
  are chosen to match CollectionSpace's own tenant identifiers exactly (see "Multi-tenancy"
  above). `verify_login()` is the actual outbound HTTP call, via `monsoon/lib/http.py:request()`
  (a truthy-success/falsy-failure wrapper, mirroring Ripley's).
- `monsoon/externals/redis.py` -- connection handling (`REDIS_USE_FAKE_CLIENT` swaps in
  `fakeredis` for tests, same pattern as Ripley) plus generic TTL'd JSON storage
  (`store_json`/`fetch_json`/`touch_key`/`delete_key`). Not CollectionSpace-specific.
- `monsoon/lib/auth.py` -- `create_session()`/`current_session()`/`destroy_session()` and a
  `login_required` decorator. The credential (username, password, instance URL) is stored in
  Redis under a random per-login token with a TTL; the Flask session cookie holds only that
  token plus the username (for display) -- never the credential itself. `current_session()`
  slides the TTL forward on every call, matching the cookie's own inactivity-based expiry.
- `monsoon/api/auth_controller.py` -- the thin `/api/auth/login`, `/logout`, `/status`
  endpoints tying the above together. Login requires a resolved tenant (`g.tenant_slug`) --
  the CollectionSpace instance URL is derived from that slug, never taken from user input.

Storing the credential in Redis rather than AWS Secrets Manager was a deliberate choice: Redis
gives native per-key TTL (Secrets Manager has none -- an abandoned browser session would
otherwise never get cleaned up), lower latency, and flat cost regardless of call volume, for a
credential that's fetched fresh on every request rather than cached. See
`docs/redis-vs-secrets-manager.md` for the full writeup of that trade-off. The value stored is
plain structured fields (username/password/instance_url/verify_ssl), not a pre-encoded HTTP
Basic Auth header -- base64 isn't encryption, and structured fields keep the username usable on
its own and keep log/secret redaction simple.

### Tools manifest
A "tool" is a self-contained feature with its own Vue route/view (the first is the Bulk Media
Uploader); which tenants can reach which tools is data, not code, so granting a tenant a new
tool is a database change, not a deploy.

- `monsoon/models/tool.py` -- `Tool` (the `tools` table: `key`/`name`) plus `tenant_tools`, a
  plain `db.Table` many-to-many association with no attributes of its own (the grant *is* the
  data). `Tool.available_for_tenant(tenant_id)` is the one query every other piece goes through.
  Seeded the same way as `tenants` -- `scripts/db/migrate/2026/20261001-MON-12/` (production),
  `tests/fixtures/tools.sql` (test), `monsoon/models/development_db.py`'s `TOOLS` list (dev via
  `flask initdb`).
- `/api/config` includes `availableTools` (an array of `{key, name}`) for the resolved tenant,
  alongside `tenantSlug` -- this is tenant-scoped data, not session-scoped, so it's available
  whether or not anyone's logged in; only the frontend's tool list gates display on being logged in.
- Frontend: `src/lib/tools.ts`'s `TOOL_REGISTRY` is a static map from a tool's backend `key` to
  the Vue route name and `mdi-*` icon that render it -- the backend only knows which tenants get
  which tools, not how the frontend routes to or illustrates them. `Home.vue` renders
  `config.availableTools` filtered against that map as the logged-in tenant's tool list (so an
  unmapped key is silently skipped rather than breaking the list); a logged-out tenant sees the
  login form in that same spot instead. `src/lib/auth.ts:requiresTool(toolKey)` is a per-route
  `beforeEnter` guard (same shape as Ripley's `src/lib/auth.ts`) checking both that someone's
  logged in and that the current tenant's `availableTools` includes that key; see its use on the
  `BulkMediaUploader` route in
  `src/router.ts`.

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
