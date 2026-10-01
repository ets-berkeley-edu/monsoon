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
from monsoon.externals import collectionspace


class TestInstanceUrlForSlug:

    def test_builds_from_slug_and_base_domain(self, app):
        with app.test_request_context('/'):
            assert collectionspace.instance_url_for_slug('pahma') == \
                'https://pahma.cspace-test.example.com/cspace-services'

    def test_ucbg_is_our_slug_for_the_legacy_botgarden_tenant(self, app):
        with app.test_request_context('/'):
            assert collectionspace.instance_url_for_slug('ucbg') == \
                'https://ucbg.cspace-test.example.com/cspace-services'


class TestNormalizeBaseUrl:

    def test_adds_scheme_and_services_path(self):
        assert collectionspace.normalize_base_url('bampfa.qa.collectionspace.org') == \
            'https://bampfa.qa.collectionspace.org/cspace-services'

    def test_leaves_an_existing_scheme_and_path_alone(self):
        url = 'https://bampfa.qa.collectionspace.org/cspace-services'
        assert collectionspace.normalize_base_url(url) == url

    def test_strips_trailing_slash(self):
        assert collectionspace.normalize_base_url('https://bampfa.qa.collectionspace.org/') == \
            'https://bampfa.qa.collectionspace.org/cspace-services'


class TestVerifyLogin:

    def test_valid_login(self, app, requests_mock):
        requests_mock.get('https://cs.example.edu/cspace-services/accounts/0/accountperms', status_code=200)
        with app.test_request_context('/'):
            ok, error = collectionspace.verify_login('https://cs.example.edu/cspace-services', 'alice', 'secret', True)
        assert ok is True
        assert error is None

    def test_invalid_credentials(self, app, requests_mock):
        requests_mock.get('https://cs.example.edu/cspace-services/accounts/0/accountperms', status_code=401)
        with app.test_request_context('/'):
            ok, error = collectionspace.verify_login('https://cs.example.edu/cspace-services', 'alice', 'wrong', True)
        assert ok is False
        assert 'Invalid username or password' in error

    def test_unreachable_instance(self, app, requests_mock):
        import requests
        requests_mock.get(
            'https://cs.example.edu/cspace-services/accounts/0/accountperms',
            exc=requests.exceptions.ConnectionError,
        )
        with app.test_request_context('/'):
            ok, error = collectionspace.verify_login('https://cs.example.edu/cspace-services', 'alice', 'secret', True)
        assert ok is False
        assert 'Could not reach' in error
