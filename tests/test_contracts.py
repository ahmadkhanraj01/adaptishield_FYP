"""
The backend contracts must stay valid and must agree with the engine.

The backend does not exist yet, so nothing else would notice if the design drifted
away from the code it wraps. These tests read files only: no database, no model.
"""
import inspect
import json
import re
from pathlib import Path

import jsonschema
import pytest
import yaml

from adaptishield_pipeline import AdaptiShieldPipeline, PipelineConfig

ROOT = Path(__file__).resolve().parent.parent
CONTRACTS = ROOT / "backend" / "contracts"

EPISODE_ID = "b7e2c1d4-8a1f-4c3e-9b6d-2f7a1c0e5d11"
TIME = "2026-12-01T09:14:22Z"


@pytest.fixture(scope="module")
def spec():
    return yaml.safe_load((CONTRACTS / "openapi.yaml").read_text())


@pytest.fixture(scope="module")
def event_schema():
    return json.loads((CONTRACTS / "stage_event.schema.json").read_text())


@pytest.fixture(scope="module")
def sql():
    return (CONTRACTS / "schema.sql").read_text()


def event(stage, verdict, detail=None, seq=0):
    return {"type": "stage_event", "episode_id": EPISODE_ID, "seq": seq,
            "stage": stage, "verdict": verdict, "detail": detail or {},
            "timestamp": TIME}


def sql_choices(sql, column):
    """The values a CHECK (column IN (...)) constraint allows."""
    match = re.search(rf"\b{column}\b[^,]*?\bIN\s*\((.*?)\)", sql, re.S)
    assert match, f"no CHECK ... IN for {column}"
    return set(re.findall(r"'([^']+)'", match.group(1)))


class TestOpenApi:
    # Architecture.md section 6: the list Phase.md says the contract must cover.
    ARCHITECTURE_ENDPOINTS = {
        ("post", "/api/auth/login"), ("post", "/api/episodes"),
        ("get", "/api/episodes"), ("get", "/api/episodes/{id}"),
        ("post", "/api/agent/run"), ("get", "/api/attacks"),
        ("post", "/api/attacks"), ("post", "/api/attack-lab/compare"),
        ("post", "/api/attack-lab/batch"), ("get", "/api/proposals"),
        ("get", "/api/proposals/{id}"), ("post", "/api/proposals/{id}/decision"),
        ("get", "/api/policy"), ("get", "/api/analytics/summary"),
        ("get", "/api/health"),
    }

    def operations(self, spec):
        return {(method, path): op
                for path, item in spec["paths"].items()
                for method, op in item.items()}

    def test_covers_every_architecture_endpoint(self, spec):
        assert set(self.operations(spec)) == self.ARCHITECTURE_ENDPOINTS

    def test_only_login_and_health_are_public(self, spec):
        # Rules.md section 4.
        public = {key for key, op in self.operations(spec).items()
                  if op.get("security") == []}
        assert public == {("post", "/api/auth/login"), ("get", "/api/health")}

    def test_only_admins_touch_proposals(self, spec):
        # Rules.md section 3: the server enforces this, so the contract must say it.
        for (_, path), op in self.operations(spec).items():
            if path.startswith("/api/proposals"):
                assert op["x-roles"] == ["admin"], path

    def test_every_operation_names_roles_and_a_phase(self, spec):
        for key, op in self.operations(spec).items():
            assert op["x-phase"] in (2, 3), key
            assert op["x-roles"], key

    def test_every_local_reference_resolves(self, spec):
        text = (CONTRACTS / "openapi.yaml").read_text()
        for ref in set(re.findall(r"#/([\w/.-]+)", text)):
            node = spec
            for part in ref.split("/"):
                assert part in node, f"broken reference: {ref}"
                node = node[part]

    def test_a_web_request_can_never_carry_a_command(self, spec):
        # Layer 4 can execute `command` in a sandbox. Nothing web-facing may reach it.
        fields = spec["components"]["schemas"]["EpisodeCreate"]["properties"]
        assert "command" not in fields
        assert spec["components"]["schemas"]["EpisodeCreate"]["additionalProperties"] is False


class TestStageEvents:
    def validate(self, schema, message):
        jsonschema.validate(message, schema)

    def test_schema_is_itself_valid(self, event_schema):
        jsonschema.Draft202012Validator.check_schema(event_schema)

    def test_takeover_event_is_accepted(self, event_schema):
        probe = {"severities": [2, 2], "actions": ["forward_email"]}
        self.validate(event_schema, event("causal_check", "takeover", {
            "ace": 0.0, "ie": 2.0, "de": 0.0, "rule": "standalone", "reason": "r",
            "probes": {"orig": probe, "masked": probe,
                       "masked_sanitized": probe, "orig_sanitized": probe}}))

    def test_final_event_must_say_whether_the_tool_may_run(self, event_schema):
        # The engine can return approved_* after Layer 4 denied the action.
        self.validate(event_schema, event("final", "pass", {
            "final_status": "approved_direct", "tool_may_run": False}))
        with pytest.raises(jsonschema.ValidationError):
            self.validate(event_schema, event("final", "pass", {
                "final_status": "approved_direct"}))

    @pytest.mark.parametrize("stage,verdict", [
        ("policy", "takeover"), ("causal_check", "block"),
        ("sanitizer", "pass"), ("sandbox", "pass"), ("received", "skip"),
    ])
    def test_a_stage_cannot_send_another_stages_verdict(self, event_schema, stage, verdict):
        with pytest.raises(jsonschema.ValidationError):
            self.validate(event_schema, event(stage, verdict))

    def test_unknown_detail_fields_are_rejected(self, event_schema):
        with pytest.raises(jsonschema.ValidationError):
            self.validate(event_schema, event("policy", "route", {"run_a_action": "x"}))

    def test_other_message_types(self, event_schema):
        self.validate(event_schema, {"type": "auth", "token": "t"})
        self.validate(event_schema, {"type": "auth_ok", "role": "analyst"})
        self.validate(event_schema, {"type": "error", "code": "too_slow", "message": "m"})
        self.validate(event_schema, {"type": "batch_progress", "batch_id": EPISODE_ID,
                                     "done": 1, "total": 2, "attack_succeeded": 0,
                                     "attack_stopped": 1})


class TestContractsAgree:
    """One vocabulary across the API, the event stream, the database and the engine."""

    def test_final_statuses_match_what_the_engine_returns(self, spec, event_schema, sql):
        source = inspect.getsource(AdaptiShieldPipeline.process_request)
        engine = set(re.findall(r'"status":\s*"(\w+)"', source))
        assert engine == set(spec["components"]["schemas"]["FinalStatus"]["enum"])
        assert engine == set(event_schema["$defs"]["final_status"]["enum"])
        assert engine == sql_choices(sql, "final_status")

    def test_setups_exist_in_pipeline_config(self, spec, event_schema, sql):
        setups = set(spec["components"]["schemas"]["Config"]["enum"])
        assert setups == set(event_schema["$defs"]["detail_received"]
                             ["properties"]["config"]["enum"])
        assert setups == sql_choices(sql, "config")
        # Each setup is a PipelineConfig method. Spotlighting's default variant is
        # datamarking, which is the variant Phase 10 measured.
        for name in setups:
            assert isinstance(getattr(PipelineConfig, name)(), PipelineConfig), name

    def test_stages_and_verdicts_match_the_database(self, event_schema, sql):
        assert set(event_schema["$defs"]["stage"]["enum"]) == sql_choices(sql, "stage")
        verdicts = event_schema["$defs"]["stage_event"]["properties"]["verdict"]["enum"]
        assert set(verdicts) == sql_choices(sql, "verdict")

    def test_roles_match_the_database(self, spec, event_schema, sql):
        roles = set(spec["components"]["schemas"]["Role"]["enum"])
        assert roles == set(event_schema["$defs"]["role"]["enum"])
        assert roles == sql_choices(sql, "role")

    def test_episode_states_and_origins_match_the_database(self, spec, sql):
        schemas = spec["components"]["schemas"]
        assert set(schemas["EpisodeState"]["enum"]) == sql_choices(sql, "state")
        assert set(schemas["Origin"]["enum"]) == sql_choices(sql, "origin")
        assert set(schemas["ActionSource"]["enum"]) == sql_choices(sql, "action_source")

    def test_evidence_fields_exist_in_layer5(self, spec):
        # The Admin Console shows what governance recomputes, so the names must match.
        from dataclasses import fields
        from layer5.governance import Evidence
        real = {f.name for f in fields(Evidence)} | {"is_regression", "is_neutral"}
        contract = set(spec["components"]["schemas"]["Evidence"]["properties"])
        assert contract <= real, contract - real

    def test_approvals_are_protected_in_the_database(self, sql):
        assert re.search(r"BEFORE UPDATE OR DELETE ON approvals", sql)
        assert re.search(r"BEFORE TRUNCATE ON approvals", sql)
