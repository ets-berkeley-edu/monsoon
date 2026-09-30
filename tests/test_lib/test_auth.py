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
from monsoon.api.errors import UnauthorizedRequestError
from monsoon.lib.auth import create_session, current_session, destroy_session, login_required
import pytest


class TestSessionLifecycle:
    """create_session/current_session/destroy_session, backed by fakeredis in tests."""

    def test_no_session_by_default(self, app, db_session):
        with app.test_request_context('/'):
            assert current_session() is None

    def test_create_and_read_back(self, app, db_session):
        with app.test_request_context('/'):
            create_session('pahma', 'https://pahma.qa.collectionspace.org/cspace-services', 'alice', 'secret', True)
            creds = current_session()
            assert creds['tenant_slug'] == 'pahma'
            assert creds['username'] == 'alice'
            assert creds['password'] == 'secret'
            assert creds['verify_ssl'] is True

    def test_destroy_clears_session(self, app, db_session):
        with app.test_request_context('/'):
            create_session('pahma', 'https://pahma.qa.collectionspace.org/cspace-services', 'alice', 'secret', True)
            destroy_session()
            assert current_session() is None


class TestLoginRequired:

    def test_rejects_when_not_logged_in(self, app, db_session):
        @login_required
        def protected_view():
            return 'ok'

        with app.test_request_context('/'):
            with pytest.raises(UnauthorizedRequestError):
                protected_view()

    def test_allows_when_logged_in(self, app, db_session):
        @login_required
        def protected_view():
            return 'ok'

        with app.test_request_context('/'):
            create_session('pahma', 'https://pahma.qa.collectionspace.org/cspace-services', 'alice', 'secret', True)
            assert protected_view() == 'ok'
