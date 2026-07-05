-- 1. Table for your nested Agile planning tree
create table if not exists epic_state_store (
    workspace_key text primary key,
    state_json jsonb not null,
    updated_at timestamptz not null default now()
);

-- 2. Table for your operational logging telemetry
create table if not exists workspace_state_logs (
    id text primary key,
    timestamp timestamptz not null default now(),
    payload jsonb not null
);

-- 3. Safety constraint to prevent future data duplication
alter table workspace_state_logs
  add constraint workspace_state_logs_id_key unique (id);
