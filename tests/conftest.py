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

import os

import monsoon.factory
import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

os.environ['MONSOON_ENV'] = 'test'


@pytest.fixture(scope='session')
def app(request):
    """Fixture application object, shared by all tests."""
    _app = monsoon.factory.create_app()

    # Create app context before running tests.
    ctx = _app.app_context()
    ctx.push()

    def teardown():
        # Pop the context after running tests.
        ctx.pop()

    request.addfinalizer(teardown)
    return _app


@pytest.fixture(scope='session')
def db(app):
    """Fixture database object, shared by all tests."""
    from monsoon import db as _db, std_commit
    from monsoon.models import development_db

    # Drop all tables before re-loading the schema.
    # If we dropped at teardown instead, an interrupted test run would block the next test run.
    development_db.clear()
    development_db.load(create_test_data=False)

    fixtures_path = f"{app.config['BASE_DIR']}/tests/fixtures"
    with open(f'{fixtures_path}/tenants.sql', 'r') as sql_file:
        _db.session.execute(text(sql_file.read()))
        std_commit(allow_test_environment=True)

    return _db


@pytest.fixture(scope='function', autouse=True)
def db_session(db):
    """Fixture database session used for the scope of a single test.

    All executions are wrapped in a session and then rolled back to keep individual tests isolated.
    """
    db.session.rollback()
    try:
        bind = db.session.get_bind()
        if isinstance(bind, Engine):
            bind.dispose()
        else:
            bind.close()
    except TypeError:
        pass
    db.session.remove()

    connection = db.engine.connect()
    _session = scoped_session(sessionmaker(bind=connection))
    db.session = _session

    return _session
