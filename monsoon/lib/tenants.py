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


def resolve_tenant_slug(host, base_domain):
    """Extract a tenant slug from a request's Host header.

    `host` is expected to look like `<slug>.<base_domain>`, with or without a trailing
    `:<port>` (e.g. `pahma.lvh.me:8080` in local development, `pahma.webapps.cspace.berkeley.edu`
    in production). Returns None if `base_domain` isn't configured, or if `host` is the bare
    apex domain or doesn't match it at all (an unrecognized host).

    This same function runs unchanged in every environment; only the configured
    `base_domain` differs (see TENANT_BASE_DOMAIN in config/*.py).
    """
    if not base_domain:
        return None
    hostname = host.split(':')[0].lower()
    suffix = f'.{base_domain.lower()}'
    if hostname.endswith(suffix) and len(hostname) > len(suffix):
        return hostname[:-len(suffix)]
    return None
