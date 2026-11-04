# agent

**Status:** not built yet (Phase 3 in [Phase.md](../Phase.md)).

Module 1, the Protected Demo Agent: a small email and document assistant with a mock mailbox and simulated tools. It proposes actions, and every proposed action goes through the Defense Engine before any tool runs. Its tools only log what would have happened ([Rules.md](../Rules.md) §5).

It must check `tool_may_run` in the engine's result, not only the status, because the engine can report an approved status after Layer 4 denied the action.
