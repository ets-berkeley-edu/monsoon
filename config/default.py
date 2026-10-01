"""
Copyright ©2026. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

import logging
import os

# Base directory for the application (one level up from this config file).
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# A tenant's CollectionSpace instance URL is constructed as "<slug>.<base-domain>", not
# stored -- see monsoon/externals/collectionspace.py:instance_url_for_slug(). This default is
# the QA tier, used for local development and dev/qa deployments alike; override to
# "collectionspace.org" in production's local config.
COLLECTIONSPACE_BASE_DOMAIN = 'qa.collectionspace.org'

# Verify TLS certs when calling a tenant's CollectionSpace instance. Only disable per-tenant,
# in a local override, for a self-hosted/sandbox instance with a self-signed certificate.
COLLECTIONSPACE_VERIFY_SSL = True

# Minutes of inactivity before session cookie is destroyed. Also used as the TTL for a logged-in
# user's CollectionSpace credential in Redis -- see monsoon/lib/auth.py.
INACTIVE_SESSION_LIFETIME = 120

# This "INDEX_HTML" default is good once deployed. See development.py for local configs.
INDEX_HTML = 'dist/static/index.html'

# Logging
LOGGING_FORMAT = '[%(asctime)s] - %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
LOGGING_LOCATION = 'monsoon.log'
LOGGING_LEVEL = logging.DEBUG
LOGGING_PROPAGATION_LEVEL = logging.WARN

# Redis holds a logged-in user's CollectionSpace credential for the life of their session (see
# monsoon/externals/redis.py, monsoon/lib/auth.py) -- never the Flask session cookie itself.
REDIS_HOST = 'localhost'
REDIS_PASSWORD = ''
REDIS_PORT = 6379
REDIS_USE_FAKE_CLIENT = False

# Used to encrypt session cookie.
SECRET_KEY = 'secret'

# Override in local configs for a real deployment.
SQLALCHEMY_DATABASE_URI = 'postgresql://monsoon:monsoon@localhost:5432/monsoon'

# A request's Host header is expected to look like "<tenant-slug>.<TENANT_BASE_DOMAIN>".
# None disables tenant resolution (every request is treated as tenant-less).
TENANT_BASE_DOMAIN = 'webapps.cspace.berkeley.edu'

TIMEZONE = 'America/Los_Angeles'

# This should only be non-None in the "local" env, where the Vue front-end runs on its own
# (Vite dev server) port instead of being served from INDEX_HTML.
VUE_LOCALHOST_PORT = None

# We keep these out of alphabetical sort above for readability's sake.
HOST = '0.0.0.0'
PORT = 5000
