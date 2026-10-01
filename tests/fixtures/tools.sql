-- The same tools manifest seeded in development (monsoon/models/development_db.py) and
-- production (scripts/db/migrate/2026/20261001-MON-12/create_tools_tables.sql): a single
-- "bulk_media_uploader" tool, available to all five tenants.

INSERT INTO tools (key, name, created_at, updated_at)
VALUES
    ('bulk_media_uploader', 'Bulk Media Uploader', now(), now());

INSERT INTO tenant_tools (tenant_id, tool_id)
SELECT tenants.id, tools.id
FROM tenants
CROSS JOIN tools
WHERE tools.key = 'bulk_media_uploader';
