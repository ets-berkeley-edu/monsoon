# Monsoon

Monsoon is a from-scratch reimplementation of
[cspace-webapps-common](https://github.com/ets-berkeley-edu/cspace-webapps-common), the
multi-tenant framework that powers UC Berkeley's CollectionSpace (CSpace)
public-facing web apps (bampfa, cinefiles, pahma, ucbg, ucjeps, and others — see
https://webapps.cspace.berkeley.edu). Monsoon's tenant slugs match CollectionSpace's own tenant
identifiers, which don't always match the legacy implementation's names — `ucbg` (UC Botanical
Garden) is `botgarden` there.

## Status

Flask + Vue.js scaffolding with subdomain-based multi-tenancy and a basic login flow. There is
intentionally no CalNet integration and no `authorized_users` table — a login is just a
CollectionSpace username/password, verified directly against the current tenant's
CollectionSpace instance and held server-side (in Redis, not the session cookie) for the
lifetime of the browser session. See the "Logging in" section below.

## Installation

* Install Python 3
* Create your virtual environment (venv)
* Install dependencies

```
pip3 install -r requirements.txt [--upgrade]
```

### Front-end dependencies

```
nvm use
npm install
```

## Database

### Create Postgres user and databases

```
createuser monsoon --no-createdb --no-superuser --no-createrole --pwprompt
createdb monsoon --owner=monsoon
createdb monsoon_test --owner=monsoon

# Load schema and seed the five known tenants
export FLASK_APP=application.py
flask initdb
```

`flask initdb` seeds the `tenants` table with the same five museums in every environment —
see the "Working with tenants locally" section below. Changes to an already-deployed
database (production) go through a hand-applied SQL file under `scripts/db/migrate/`, not
through `flask initdb` — see `scripts/db/schema.sql` for the current cumulative schema and
`scripts/db/migrate/2026/20260924-MON-6/` for an example.

## Redis

A logged-in user's CollectionSpace credential lives in Redis (with a TTL), not the session
cookie — see the "Logging in" section below.

### Local Redis Server installation (optional)

```
brew install redis

# Start server
redis-server
```

Tests use a fake in-memory Redis client (`REDIS_USE_FAKE_CLIENT`, see `config/test.py`) and
don't need a real server running.

## Run the app

```
# Backend (Flask), on port 5000
python3 application.py

# Front end (Vite dev server), on port 8080
npm run serve-vue
```

With both running, visit http://localhost:8080.

## Working with tenants locally

Monsoon is multi-tenant: which museum a request is for gets resolved from the subdomain of
the request's Host header (e.g. `pahma.webapps.cspace.berkeley.edu` in production), not from
a path or query param. Locally, that same resolution logic runs against `localhost` instead —
per RFC 6761, `localhost` and all of its subdomains resolve to the loopback address, and
browsers honor that natively, so `<slug>.localhost` behaves like a tenant subdomain with no
`/etc/hosts` editing or other local setup required.

With both dev servers running as above, visit a tenant at, e.g.:

```
http://pahma.localhost:8080
http://ucbg.localhost:8080
```

instead of plain `http://localhost:8080`. The Flask backend (port 5000) resolves the same way,
so API requests made from the Vite dev server stay on the same tenant subdomain end to end.
Visiting bare `http://localhost:8080` is a valid request with no tenant resolved — the same as
an apex-domain request in production.

This is configured via `TENANT_BASE_DOMAIN` in `config/development.py`; nothing about the
resolution code itself differs between development and production, only that config value.

Only the five tenants seeded by `flask initdb` (bampfa, cinefiles, pahma, ucbg, ucjeps) are
recognized — a subdomain that doesn't match a row in the `tenants` table (e.g.
`nope.localhost:8080`) gets a 404, regardless of environment.

## Logging in

Visiting a tenant subdomain (e.g. `pahma.localhost:8080`) shows a CollectionSpace
username/password form. Logging in makes one real call to that tenant's CollectionSpace
instance (`GET /accounts/0/accountperms`) to verify the credential; there's no separate
Monsoon-side account or password of any kind.

A tenant's CollectionSpace instance URL is never stored — it's built at request time from the
tenant's slug plus `COLLECTIONSPACE_BASE_DOMAIN` (`monsoon/externals/collectionspace.py:
instance_url_for_slug()`), e.g. `pahma` + `qa.collectionspace.org` →
`https://pahma.qa.collectionspace.org`. `config/default.py` defaults this to CollectionSpace's
QA tier, used for both local development and dev/qa deployments; production overrides it to
`collectionspace.org` via local config.

This construction only works because our tenant slugs are chosen to match CollectionSpace's own
tenant identifiers exactly — unlike the legacy cspace-webapps-common implementation's names.
The one case where they differ: Monsoon's `ucbg` tenant (UC Botanical Garden) is
cspace-webapps-common's `botgarden`.

`monsoon/lib/auth.py` and `monsoon/externals/{redis,collectionspace}.py` are where the rest of
this lives: the credential is stored in Redis under a random per-login token (with a TTL
matching `INACTIVE_SESSION_LIFETIME`), and only that token — never the credential — goes in the
Flask session cookie. Logging out deletes the Redis key immediately.

## Tools

Once logged in, the home page lists whatever tools the current tenant has access to — for now,
just the Bulk Media Uploader, available to all five tenants. Which tenants can reach which
tools is a database manifest (the `tools` and `tenant_tools` tables, `monsoon/models/tool.py`),
not a code change — see `flask initdb`'s seed data in `monsoon/models/development_db.py` for the
current grants. A tool with no grant for the current tenant is both hidden from that list and
rejected if its route is visited directly. The account menu (logged-in username, with a log-out
option) lives in the app bar's upper right and persists across tool pages; clicking "Monsoon" at
upper left always returns to the tenant's home page.

## Run tests, lint the code

We use [Tox](https://tox.readthedocs.io) for continuous integration.
Under the hood, you'll find [PyTest](https://docs.pytest.org), [Ruff](https://github.com/astral-sh/ruff) and [ESLint](https://eslint.org/).
```
# Run tests and linters in parallel:
tox -p

# Pytest
tox -e test

# Linters, à la carte
tox -e lint-py
tox -e lint-vue

# Auto-fix linting errors in Vue code
tox -e lint-vue-fix
```
