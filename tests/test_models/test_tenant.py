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
from monsoon.models.tenant import Tenant


class TestTenant:
    """The tenants fixture (tests/fixtures/tenants.sql) seeds the five known museum tenants."""

    def test_get_all(self, db_session):
        slugs = [tenant.slug for tenant in Tenant.get_all()]
        assert slugs == ['bampfa', 'botgarden', 'cinefiles', 'pahma', 'ucjeps']

    def test_find_by_slug(self, db_session):
        tenant = Tenant.find_by_slug('pahma')
        assert tenant.name == 'Phoebe A. Hearst Museum of Anthropology'

    def test_find_by_slug_unrecognized(self, db_session):
        assert Tenant.find_by_slug('not-a-real-tenant') is None

    def test_to_api_json(self, db_session):
        api_json = Tenant.find_by_slug('bampfa').to_api_json()
        assert api_json['slug'] == 'bampfa'
        assert api_json['name'] == 'Berkeley Art Museum and Pacific Film Archive'
        assert api_json['createdAt']
        assert api_json['updatedAt']
