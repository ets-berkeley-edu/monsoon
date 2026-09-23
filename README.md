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

## Run tests, lint the code

*To be filled in as the project takes shape.*
