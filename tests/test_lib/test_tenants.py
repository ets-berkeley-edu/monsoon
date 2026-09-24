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
from monsoon.lib.tenants import resolve_tenant_slug


class TestResolveTenantSlug:
    """Tenant resolution from a request's Host header."""

    def test_simple_subdomain(self):
        """A tenant subdomain resolves to its slug."""
        assert resolve_tenant_slug('pahma.webapps.cspace.berkeley.edu', 'webapps.cspace.berkeley.edu') == 'pahma'

    def test_local_dev_domain_with_port(self):
        """A port on the Host header (as in local dev) doesn't confuse resolution."""
        assert resolve_tenant_slug('botgarden.localhost:8080', 'localhost') == 'botgarden'

    def test_is_case_insensitive(self):
        """Host headers are matched case-insensitively."""
        assert resolve_tenant_slug('PAHMA.WEBAPPS.CSPACE.BERKELEY.EDU', 'webapps.cspace.berkeley.edu') == 'pahma'

    def test_apex_domain_has_no_tenant(self):
        """A request for the bare base domain (no subdomain) resolves to no tenant."""
        assert resolve_tenant_slug('webapps.cspace.berkeley.edu', 'webapps.cspace.berkeley.edu') is None

    def test_unrecognized_host_has_no_tenant(self):
        """A Host header that doesn't match the configured base domain resolves to no tenant."""
        assert resolve_tenant_slug('example.com', 'webapps.cspace.berkeley.edu') is None

    def test_missing_base_domain_has_no_tenant(self):
        """When TENANT_BASE_DOMAIN isn't configured, tenant resolution is disabled entirely."""
        assert resolve_tenant_slug('pahma.webapps.cspace.berkeley.edu', None) is None
