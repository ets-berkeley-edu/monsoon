-- MON-6: create the tenants table and seed it with the five known museum tenants.
--
-- Run by hand against the target database (psql), same as any other file under
-- scripts/db/migrate/. Not applied by any automated tooling. schema.sql is kept in sync
-- separately to reflect the cumulative current state for fresh databases.
--
-- Monsoon's tenant slugs are chosen to match CollectionSpace's own tenant identifiers exactly,
-- so a tenant's CollectionSpace instance URL can be constructed as "<slug>.<base-domain>" with
-- no per-tenant exceptions (see monsoon/externals/collectionspace.py:instance_url_for_slug()).
-- CollectionSpace's identifier for UC Botanical Garden is "ucbg", not "botgarden" -- the name
-- the legacy cspace-webapps-common implementation uses for that same tenant.

CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(80) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

INSERT INTO tenants (slug, name, created_at, updated_at)
VALUES
    ('bampfa', 'Berkeley Art Museum and Pacific Film Archive', now(), now()),
    ('cinefiles', 'CineFiles', now(), now()),
    ('pahma', 'Phoebe A. Hearst Museum of Anthropology', now(), now()),
    ('ucbg', 'UC Botanical Garden', now(), now()),
    ('ucjeps', 'University and Jepson Herbaria', now(), now());
