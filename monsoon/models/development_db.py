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
from monsoon import db, std_commit
from monsoon.models.tenant import Tenant
from sqlalchemy import text

# The known museum tenants -- see the "Working with tenants locally" section of README.md.
# Kept in sync with scripts/db/migrate/2026/20260924-MON-6/create_tenants_table.sql (the
# production migration) and tests/fixtures/tenants.sql (the test fixture); all three are
# expected to define the same five tenants.
TENANTS = [
    ('bampfa', 'Berkeley Art Museum and Pacific Film Archive'),
    ('botgarden', 'UC Botanical Garden'),
    ('cinefiles', 'CineFiles'),
    ('pahma', 'Phoebe A. Hearst Museum of Anthropology'),
    ('ucjeps', 'University and Jepson Herbaria'),
]


def clear():
    with open(f"{app.config['BASE_DIR']}/scripts/db/drop_schema.sql", 'r') as ddl_file:
        db.session.execute(text(ddl_file.read()))
        # Schema DDL should never be left as an uncommitted, rollback-able change, even in tests.
        std_commit(allow_test_environment=True)


def load(create_test_data=True):
    _load_schema()
    if create_test_data:
        _create_tenants()
    return db


def _load_schema():
    """Create DB schema from SQL file."""
    with open(f"{app.config['BASE_DIR']}/scripts/db/schema.sql", 'r') as ddl_file:
        db.session.execute(text(ddl_file.read()))
        std_commit(allow_test_environment=True)


def _create_tenants():
    for slug, name in TENANTS:
        Tenant.create(slug=slug, name=name)
