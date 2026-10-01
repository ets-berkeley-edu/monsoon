-- MON-12: create the tools table and the tenant_tools join table, seeding a single tool
-- ("bulk_media_uploader") available to all five tenants.
--
-- A tool is a self-contained feature of the app (its own Vue route/view); which tenants can
-- reach it is data, not code, so new tools and tenant grants can be added without a deploy.
--
-- Run by hand against the target database (psql), same as any other file under
-- scripts/db/migrate/.

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

INSERT INTO tools (key, name, created_at, updated_at)
VALUES
    ('bulk_media_uploader', 'Bulk Media Uploader', now(), now());

-- Available to all five tenants.
INSERT INTO tenant_tools (tenant_id, tool_id)
SELECT tenants.id, tools.id
FROM tenants
CROSS JOIN tools
WHERE tools.key = 'bulk_media_uploader';
