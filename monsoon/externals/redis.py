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
from fakeredis import FakeStrictRedis
from flask import current_app as app
import redis as redis_client
import simplejson as json

_redis_conn = None


def get_redis_conn():
    global _redis_conn
    if _redis_conn is None:
        if app.config['REDIS_USE_FAKE_CLIENT']:
            _redis_conn = FakeStrictRedis()
        elif app.config['REDIS_PASSWORD']:
            _redis_conn = redis_client.from_url(get_url())
        else:
            _redis_conn = redis_client.from_url(f"redis://{app.config['REDIS_HOST']}:{app.config['REDIS_PORT']}")
    return _redis_conn


def get_url():
    return f"rediss://default:{app.config['REDIS_PASSWORD']}@{app.config['REDIS_HOST']}:{app.config['REDIS_PORT']}"


def store_json(key, value, expire_seconds=None):
    conn = get_redis_conn()
    conn.set(key, json.dumps(value))
    if expire_seconds:
        conn.expire(key, expire_seconds)


def fetch_json(key):
    value = get_redis_conn().get(key)
    return None if value is None else json.loads(value)


def touch_key(key, expire_seconds):
    """Reset a key's TTL, e.g. to slide an active session's expiry forward on use."""
    get_redis_conn().expire(key, expire_seconds)


def delete_key(key):
    get_redis_conn().delete(key)
