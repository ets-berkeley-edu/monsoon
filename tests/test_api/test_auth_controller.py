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
PAHMA_HOST = 'pahma.monsoon-test.example.com'
ACCOUNTPERMS_URL = 'https://pahma.cspace-test.example.com/cspace-services/accounts/0/accountperms'


class TestLogin:

    def test_requires_a_tenant(self, client):
        response = client.post('/api/auth/login', json={'username': 'alice', 'password': 'secret'})
        assert response.status_code == 400

    def test_requires_username_and_password(self, client):
        response = client.post('/api/auth/login', json={}, headers={'Host': PAHMA_HOST})
        assert response.status_code == 400

    def test_invalid_credentials(self, client, requests_mock):
        requests_mock.get(ACCOUNTPERMS_URL, status_code=401)
        response = client.post(
            '/api/auth/login',
            json={'username': 'alice', 'password': 'wrong'},
            headers={'Host': PAHMA_HOST},
        )
        assert response.status_code == 401
        assert 'Invalid username or password' in response.json['message']

    def test_successful_login(self, client, requests_mock):
        requests_mock.get(ACCOUNTPERMS_URL, status_code=200)
        response = client.post(
            '/api/auth/login',
            json={'username': 'alice', 'password': 'secret'},
            headers={'Host': PAHMA_HOST},
        )
        assert response.status_code == 200
        assert response.json['username'] == 'alice'


class TestStatus:

    def test_status_when_logged_out(self, client):
        response = client.get('/api/auth/status', headers={'Host': PAHMA_HOST})
        assert response.status_code == 200
        assert response.json['username'] is None

    def test_status_after_login(self, client, requests_mock):
        requests_mock.get(ACCOUNTPERMS_URL, status_code=200)
        client.post(
            '/api/auth/login',
            json={'username': 'alice', 'password': 'secret'},
            headers={'Host': PAHMA_HOST},
        )
        response = client.get('/api/auth/status', headers={'Host': PAHMA_HOST})
        assert response.json['username'] == 'alice'


class TestLogout:

    def test_logout_clears_the_session(self, client, requests_mock):
        requests_mock.get(ACCOUNTPERMS_URL, status_code=200)
        client.post(
            '/api/auth/login',
            json={'username': 'alice', 'password': 'secret'},
            headers={'Host': PAHMA_HOST},
        )
        client.post('/api/auth/logout', headers={'Host': PAHMA_HOST})
        response = client.get('/api/auth/status', headers={'Host': PAHMA_HOST})
        assert response.json['username'] is None
