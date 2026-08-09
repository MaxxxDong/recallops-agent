CREATE TABLE IF NOT EXISTS incidents (
  incident_id UUID PRIMARY KEY,
  service STRING NOT NULL,
  severity STRING NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS incident_events (
  event_id UUID PRIMARY KEY,
  incident_id UUID NOT NULL REFERENCES incidents (incident_id),
  event_text STRING NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS agent_runs (
  run_id UUID PRIMARY KEY,
  incident_id UUID NOT NULL REFERENCES incidents (incident_id),
  state JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS run_checkpoints (
  checkpoint_id UUID PRIMARY KEY,
  run_id UUID NOT NULL REFERENCES agent_runs (run_id),
  status STRING NOT NULL,
  state JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS action_receipts (
  idempotency_key STRING PRIMARY KEY,
  run_id UUID NOT NULL REFERENCES agent_runs (run_id),
  receipt JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS approvals (
  approval_id UUID PRIMARY KEY,
  run_id UUID NOT NULL REFERENCES agent_runs (run_id),
  decision STRING NOT NULL CHECK (decision IN ('approved', 'rejected')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS audit_events (
  audit_id UUID PRIMARY KEY,
  run_id UUID NOT NULL REFERENCES agent_runs (run_id),
  event_type STRING NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
