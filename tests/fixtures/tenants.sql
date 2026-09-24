-- The same five tenants seeded in development (monsoon/models/development_db.py) and
-- production (scripts/db/migrate/2026/20260924-MON-6/create_tenants_table.sql).

INSERT INTO tenants (slug, name, created_at, updated_at)
VALUES
    ('bampfa', 'Berkeley Art Museum and Pacific Film Archive', now(), now()),
    ('botgarden', 'UC Botanical Garden', now(), now()),
    ('cinefiles', 'CineFiles', now(), now()),
    ('pahma', 'Phoebe A. Hearst Museum of Anthropology', now(), now()),
    ('ucjeps', 'University and Jepson Herbaria', now(), now());
