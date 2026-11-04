-- AdaptiShield database design (PostgreSQL 16).
--
-- This is the agreed design. The first Alembic migration must produce exactly
-- this schema; after that, changes go through Alembic (Rules.md section 4).
--
-- attacks.injected_text, episodes.user_input, episodes.tool_response and
-- stage_events.detail can hold attacker-written text. Store them as data and
-- display them as plain text only (Rules.md section 5).

CREATE TABLE users (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name          text NOT NULL,
    email         text NOT NULL UNIQUE,
    role          text NOT NULL CHECK (role IN ('tester', 'analyst', 'admin')),
    password_hash text NOT NULL,
    is_active     boolean NOT NULL DEFAULT true,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE attacks (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source          text NOT NULL CHECK (source IN ('injecagent', 'agentdojo', 'custom')),
    source_index    integer,            -- position in the imported file; NULL for custom
    suite           text,               -- AgentDojo groups by suite; it has no attack_type
    attack_type     text,               -- InjecAgent attack type, or NULL
    user_task       text NOT NULL,
    injected_text   text NOT NULL,      -- the content the agent reads
    proposed_action text,
    target          text,
    target_match    boolean,            -- can the target-match path fire? Reported separately
    is_benign       boolean NOT NULL DEFAULT false,
    created_by      uuid REFERENCES users (id),
    created_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (source, source_index)
);
CREATE INDEX attacks_source_type_idx ON attacks (source, attack_type);

CREATE TABLE episodes (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    attack_id       uuid REFERENCES attacks (id),
    origin          text NOT NULL CHECK (origin IN ('api', 'demo_agent', 'attack_lab', 'batch')),
    config          text NOT NULL CHECK (config IN ('undefended', 'spotlighting', 'full')),
    action_source   text NOT NULL CHECK (action_source IN ('supplied', 'derived')),
    state           text NOT NULL DEFAULT 'queued'
                    CHECK (state IN ('queued', 'running', 'completed', 'failed')),
    error           text,
    session_id      text NOT NULL,
    tool_name       text NOT NULL,
    user_input      text NOT NULL,
    tool_response   text NOT NULL,
    proposed_action text,               -- NULL when the agent derives the action
    final_status    text CHECK (final_status IN
                    ('approved_direct', 'approved_causal', 'safe_continuation', 'blocked')),
    tool_may_run    boolean,
    created_by      uuid NOT NULL REFERENCES users (id),
    created_at      timestamptz NOT NULL DEFAULT now(),
    started_at      timestamptz,
    finished_at     timestamptz,
    -- A completed episode has a verdict; any other state does not.
    CONSTRAINT completed_has_verdict CHECK (
        (state = 'completed') = (final_status IS NOT NULL AND tool_may_run IS NOT NULL)
    ),
    CONSTRAINT failed_has_error CHECK ((state = 'failed') = (error IS NOT NULL))
);
CREATE INDEX episodes_created_idx ON episodes (created_at);
CREATE INDEX episodes_status_idx ON episodes (final_status);
CREATE INDEX episodes_attack_idx ON episodes (attack_id);

CREATE TABLE stage_events (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    episode_id uuid NOT NULL REFERENCES episodes (id) ON DELETE RESTRICT,
    seq        integer NOT NULL CHECK (seq >= 0),
    stage      text NOT NULL CHECK (stage IN
               ('received', 'provenance', 'screener', 'policy', 'causal_check',
                'sanitizer', 'permission', 'egress', 'sandbox', 'final')),
    verdict    text NOT NULL CHECK (verdict IN
               ('pass', 'flag', 'route', 'approve', 'takeover', 'nochange',
                'strip', 'block', 'skip', 'running', 'error')),
    detail     jsonb NOT NULL DEFAULT '{}'::jsonb,
    timestamp  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (episode_id, seq)
);

CREATE TABLE proposals (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    change            jsonb NOT NULL,
    claimed_reward    double precision,  -- the proposal's own figure; never shown as evidence
    status            text NOT NULL DEFAULT 'pending'
                      CHECK (status IN ('pending', 'approved', 'rejected')),
    source_file       text NOT NULL,
    source_hash       text NOT NULL UNIQUE,
    created_at        timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE approvals (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id uuid NOT NULL UNIQUE REFERENCES proposals (id) ON DELETE RESTRICT,
    admin_id    uuid NOT NULL REFERENCES users (id) ON DELETE RESTRICT,
    decision    text NOT NULL CHECK (decision IN ('approved', 'rejected')),
    reason      text NOT NULL CHECK (length(btrim(reason)) > 0),
    evidence    jsonb NOT NULL,         -- what the server recomputed and the Admin saw
    warnings    jsonb NOT NULL DEFAULT '[]'::jsonb,
    decided_at  timestamptz NOT NULL DEFAULT now()
);

-- Approval history is append-only (Rules.md section 3). Enforce it in the
-- database, so that no application bug can rewrite who approved what. To reverse
-- a decision, approve a new proposal that undoes the change.
CREATE FUNCTION approvals_are_append_only() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'approvals is append-only: % is not allowed', TG_OP;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER approvals_no_change
    BEFORE UPDATE OR DELETE ON approvals
    FOR EACH ROW EXECUTE FUNCTION approvals_are_append_only();

CREATE TRIGGER approvals_no_truncate
    BEFORE TRUNCATE ON approvals
    FOR EACH STATEMENT EXECUTE FUNCTION approvals_are_append_only();

CREATE TABLE evaluation_runs (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    corpus      text NOT NULL,
    config      text NOT NULL,
    model_tags  jsonb NOT NULL,
    commit_sha  text NOT NULL,
    dirty       boolean NOT NULL DEFAULT false,
    metrics     jsonb NOT NULL,
    source_file text,                   -- the results/ file this row was loaded from
    created_at  timestamptz NOT NULL DEFAULT now()
);
