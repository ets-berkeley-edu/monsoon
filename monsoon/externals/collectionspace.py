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
from flask import current_app as app
from monsoon.lib import http


def instance_url_for_slug(slug):
    """Build a tenant's CollectionSpace instance URL from its slug + the configured tier.

    The instance lives at "<slug>.<COLLECTIONSPACE_BASE_DOMAIN>" -- QA
    (qa.collectionspace.org) for local dev and dev/qa deployments, collectionspace.org in
    production. Our tenant slugs are chosen to match CollectionSpace's own tenant identifiers
    exactly (e.g. "ucbg", not the legacy cspace-webapps-common name "botgarden") specifically so
    this construction needs no per-tenant override.
    """
    return normalize_base_url(f"{slug}.{app.config['COLLECTIONSPACE_BASE_DOMAIN']}")


def normalize_base_url(raw_url):
    """Turn a tenant's configured CollectionSpace URL into a usable cspace-services base URL."""
    url = raw_url.strip().rstrip('/')
    if not url.startswith('http://') and not url.startswith('https://'):
        url = f'https://{url}'
    if not url.endswith('/cspace-services'):
        url = f'{url}/cspace-services'
    return url


def verify_login(base_url, username, password, verify_ssl=True):
    """Confirm a username/password pair is a valid login for this CollectionSpace instance.

    Uses GET /accounts/0/accountperms -- csid "0" is a real, deliberate sentinel in the
    CollectionSpace services source that resolves to "whichever account is currently
    authenticated", making this a self-service "am I who I say I am" check: any valid account
    gets a clean response back, regardless of what else it does or doesn't have permission to
    do.

    Returns (True, None) on success, or (False, error_message) on failure.
    """
    response = http.request(
        f'{base_url}/accounts/0/accountperms',
        auth=(username, password),
        verify=verify_ssl,
        timeout=30,
    )
    if response:
        return True, None
    return False, _describe_failed_login(response, base_url)


def _describe_failed_login(response, base_url):
    status_code = getattr(response.raw_response, 'status_code', None)
    if status_code == 401:
        return 'Invalid username or password for this CollectionSpace instance.'
    if status_code == 404:
        return f"Couldn't find the CollectionSpace accounts service at {base_url} -- double-check the instance URL."
    if status_code and status_code >= 500:
        return f'The CollectionSpace instance returned a server error (HTTP {status_code}).'
    return f'Could not reach {base_url} to verify login: {response.exception}'
