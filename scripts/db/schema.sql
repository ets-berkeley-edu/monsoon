-- Copyright ©2026. The Regents of the University of California (Regents). All Rights Reserved.
--
-- Permission to use, copy, modify, and distribute this software and its documentation
-- for educational, research, and not-for-profit purposes, without fee and without a
-- signed licensing agreement, is hereby granted, provided that the above copyright
-- notice, this paragraph and the following two paragraphs appear in all copies,
-- modifications, and distributions.
--
-- Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
-- Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
-- http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.
--
-- IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
-- INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
-- THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
-- OF THE POSSIBILITY OF SUCH DAMAGE.
--
-- REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
-- IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
-- SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
-- "AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
-- ENHANCEMENTS, OR MODIFICATIONS.

-- This file is the canonical, cumulative schema for a fresh database (local dev or test). It is
-- run wholesale by `flask initdb` / the pytest `db` fixture, and does not seed any rows itself --
-- see monsoon/models/development_db.py (dev) and tests/fixtures/ (test) for that. Changes to an
-- already-deployed database go through scripts/db/migrate/, applied by hand; this file should be
-- kept in sync to reflect the cumulative result of those migrations.

CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(80) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

-- A tool is a self-contained feature of the app (its own Vue route/view). tenant_tools is the
-- manifest of which tenants can reach which tools.
CREATE TABLE tools (
    id SERIAL PRIMARY KEY,
    key VARCHAR(80) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE tenant_tools (
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    tool_id INTEGER NOT NULL REFERENCES tools(id),
    PRIMARY KEY (tenant_id, tool_id)
);
