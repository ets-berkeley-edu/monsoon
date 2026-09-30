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
from flask import current_app as app, g, request
from monsoon.externals import collectionspace
from monsoon.lib.auth import create_session, current_session, destroy_session
from monsoon.lib.http import tolerant_jsonify


@app.route('/api/auth/login', methods=['POST'])
def login():
    tenant_slug = g.get('tenant_slug')
    if not tenant_slug:
        return tolerant_jsonify({'message': 'Log in from a museum subdomain.'}, status=400)

    params = request.get_json(silent=True) or {}
    username = (params.get('username') or '').strip()
    password = params.get('password') or ''
    if not username or not password:
        return tolerant_jsonify({'message': 'Username and password are required.'}, status=400)

    instance_url = collectionspace.instance_url_for_slug(tenant_slug)
    verify_ssl = app.config['COLLECTIONSPACE_VERIFY_SSL']

    ok, error = collectionspace.verify_login(instance_url, username, password, verify_ssl)
    if not ok:
        return tolerant_jsonify({'message': error}, status=401)

    create_session(tenant_slug, instance_url, username, password, verify_ssl)
    return tolerant_jsonify({'username': username})


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    destroy_session()
    return tolerant_jsonify({'message': 'Logged out.'})


@app.route('/api/auth/status')
def status():
    creds = current_session()
    return tolerant_jsonify({'username': creds['username'] if creds else None})
