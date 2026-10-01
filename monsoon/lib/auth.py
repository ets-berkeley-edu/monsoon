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
from functools import wraps
import secrets

from flask import current_app as app, g, session
from monsoon.api.errors import UnauthorizedRequestError
from monsoon.externals import redis

SESSION_KEY_PREFIX = 'cs-session'


def create_session(tenant_slug, instance_url, username, password, verify_ssl):
    """Start a CollectionSpace-authenticated session for the current browser.

    The credential itself is stored in Redis, with a TTL, keyed by a random token -- the Flask
    session cookie holds only that token (plus the username, for display), never the
    credential. See the "Redis vs Secrets Manager" decision memo for why.
    """
    token = secrets.token_urlsafe(32)
    redis.store_json(_redis_key(token), {
        'tenant_slug': tenant_slug,
        'instance_url': instance_url,
        'username': username,
        'password': password,
        'verify_ssl': verify_ssl,
    }, expire_seconds=_session_ttl_seconds())

    session.clear()
    session.permanent = True
    session['cs_session_token'] = token
    session['cs_username'] = username


def destroy_session():
    """End the current browser's CollectionSpace-authenticated session, if any."""
    token = session.get('cs_session_token')
    if token:
        redis.delete_key(_redis_key(token))
    session.clear()


def current_session():
    """Return the current request's CollectionSpace credentials, or None if not logged in.

    Slides the credential's TTL forward on each call, matching the Flask session cookie's own
    inactivity-based expiry (see before_request in monsoon/routes.py) -- an active session
    shouldn't have its Redis-held credential expire out from under it on a fixed clock while the
    cookie itself is still considered current.
    """
    token = session.get('cs_session_token')
    if not token:
        return None
    creds = redis.fetch_json(_redis_key(token))
    if creds is None:
        session.clear()
        return None
    redis.touch_key(_redis_key(token), _session_ttl_seconds())
    return creds


def login_required(view):
    """Reject (401) any request without an active CollectionSpace-authenticated session."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        creds = current_session()
        if creds is None:
            raise UnauthorizedRequestError('Login required.')
        g.cs_credentials = creds
        return view(*args, **kwargs)
    return wrapped


def _redis_key(token):
    return f'{SESSION_KEY_PREFIX}:{token}'


def _session_ttl_seconds():
    return app.config['INACTIVE_SESSION_LIFETIME'] * 60
