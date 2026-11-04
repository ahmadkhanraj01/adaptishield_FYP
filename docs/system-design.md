---
hide: [navigation]
---

# System design

A FastAPI backend wraps the Defense Engine, with a React frontend, PostgreSQL storage and local models through Ollama. All of it runs on one machine, with no paid API.

## Technology

| Area | Technology |
| :--- | :--- |
| Backend | Python 3.10, FastAPI, WebSockets |
| Frontend | React, Vite, Tailwind CSS, Recharts |
| Models | Ollama on a 4 GB GPU |
| Storage | PostgreSQL |
| Packaging and quality | Docker Compose, GitHub Actions, Pytest |

## REST API

The full contract is [openapi.yaml](assets/contracts/openapi.yaml). Automated tests keep it in step with the engine.

| Endpoint | Roles | Purpose |
| :--- | :--- | :--- |
| `POST /api/auth/login` | Public | Get a token |
| `POST /api/episodes` | Tester, Admin | Queue one request through the engine |
| `GET /api/episodes` | All signed-in | List and filter episodes |
| `GET /api/episodes/{id}` | All signed-in | One episode with its stage events |
| `GET /api/attacks` | Tester, Admin | Browse the attack catalogue |
| `POST /api/attacks` | Tester, Admin | Save a custom attack |
| `POST /api/agent/run` | Tester, Admin | Run the Demo Agent |
| `POST /api/attack-lab/compare` | Tester, Admin | Run an attack with protection off and on |
| `POST /api/attack-lab/batch` | Tester, Admin | Run a whole attack type |
| `GET /api/proposals` | Admin | List configuration proposals |
| `GET /api/proposals/{id}` | Admin | One proposal with recomputed evidence |
| `POST /api/proposals/{id}/decision` | Admin | Approve or reject, with a reason |
| `GET /api/policy` | Analyst, Admin | Current rules and thresholds |
| `GET /api/analytics/summary` | Analyst, Admin | Rates with sample sizes and intervals |
| `GET /api/health` | Public | Backend, database and model status |

## Live events

`WS /ws/episodes` streams one event per stage. The exact messages are in [stage_event.schema.json](assets/contracts/stage_event.schema.json). Replay uses the same saved events, so it shows exactly what appeared live.

```json
{
  "type": "stage_event",
  "seq": 5,
  "stage": "causal_check",
  "verdict": "takeover",
  "detail": { "rule": "standalone", "ace": 0.0, "ie": 2.0, "de": 0.0 },
  "timestamp": "2026-12-01T09:14:22Z"
}
```

## Database

The exact schema is [schema.sql](assets/contracts/schema.sql). The database itself refuses any change to the approval history.

![Database tables and relationships](assets/diagrams/er.png)

## Security

| Threat | Response |
| :--- | :--- |
| Injected text runs script in an Admin's browser | Untrusted content is always displayed as plain text |
| A non-Admin approves a change | The server checks the role on every request |
| A false proposal misleads the Admin | The server recomputes the evidence, and warns when a change is worse or does nothing |
| Decision history is rewritten | Database triggers refuse updates and deletes |
| A web request reaches the sandbox | The API has no command field |
| The agent acts on an unsafe result | Tools run only if the engine reports that they may |

## Run the tests

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -q
```

The tests need no model, network or GPU.
