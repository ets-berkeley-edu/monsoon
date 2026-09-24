# Monsoon

Monsoon is a from-scratch reimplementation of
[cspace-webapps-common](https://github.com/ets-berkeley-edu/cspace-webapps-common), the
multi-tenant framework that powers UC Berkeley's CollectionSpace (CSpace)
public-facing web apps (bampfa, botgarden, cinefiles, pahma, ucjeps, and others — see
https://webapps.cspace.berkeley.edu).

## Status

Basic Flask + Vue.js scaffolding. No CollectionSpace integration yet — this just proves out
the app skeleton (backend serving a `/api/config` endpoint, front end fetching it on load).

There is intentionally no CalNet integration and no `authorized_users` table. Per the plan,
Monsoon will pass credentials through to CollectionSpace rather than handling
authentication/authorization itself.

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
http://botgarden.localhost:8080
```

instead of plain `http://localhost:8080`. The Flask backend (port 5000) resolves the same way,
so API requests made from the Vite dev server stay on the same tenant subdomain end to end.
Visiting bare `http://localhost:8080` is a valid request with no tenant resolved — the same as
an apex-domain request in production.

This is configured via `TENANT_BASE_DOMAIN` in `config/development.py`; nothing about the
resolution code itself differs between development and production, only that config value.

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
