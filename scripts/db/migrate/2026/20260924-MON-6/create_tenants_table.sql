-- MON-6: create the tenants table and seed it with the five known museum tenants.
--
-- Run by hand against the target database (psql), same as any other file under
-- scripts/db/migrate/. Not applied by any automated tooling. schema.sql is kept in sync
-- separately to reflect the cumulative current state for fresh databases.

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
    ('botgarden', 'UC Botanical Garden', now(), now()),
    ('cinefiles', 'CineFiles', now(), now()),
    ('pahma', 'Phoebe A. Hearst Museum of Anthropology', now(), now()),
    ('ucjeps', 'University and Jepson Herbaria', now(), now());
