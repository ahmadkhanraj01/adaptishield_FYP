# backend

**Status:** contracts agreed, service not built yet (Phase 2 in [Phase.md](../Phase.md)).

The FastAPI service that wraps the Defense Engine. It adds the REST API, the live WebSocket stream, login with three roles, and PostgreSQL storage. Decision logic stays in `layer*/` and `adaptishield_pipeline.py` ([Rules.md](../Rules.md) §2).

## Contracts

These files are the design every module builds against. `tests/test_contracts.py` checks that they stay valid and agree with the engine.

| File | Defines |
| :--- | :--- |
| [contracts/openapi.yaml](contracts/openapi.yaml) | Every REST endpoint, with roles and build phase |
| [contracts/stage_event.schema.json](contracts/stage_event.schema.json) | Every message on `WS /ws/episodes`, including stage events |
| [contracts/schema.sql](contracts/schema.sql) | The PostgreSQL schema that the first Alembic migration must produce |

The build plan is in `FYP/AdaptiShield_Phase2_Backend_Design.docx`.
