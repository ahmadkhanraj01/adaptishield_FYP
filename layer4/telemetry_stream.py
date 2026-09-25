import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class EpisodeRecord:
    """
    Structured record matching the schema the future Adaptive Threat
    Model (3D) will consume for GRPO training. Emitted at every
    tool-return boundary regardless of outcome.
    """
    boundary_index:        int
    tool_name:              str
    proposed_action:        str
    causal_verdict:          Optional[Dict[str, Any]] = None   # ACE/IE/DE + takeover from 3B
    screen_result:           Optional[Dict[str, Any]] = None   # from Layer 3 screener: flagged/source/matched markers
    # Truncated mediator (untrusted tool-response) content. 3D's blocked_pattern
    # learning previously had to be fed markers by the red team, because the
    # phrasing that evades 3B lives here and the record didn't keep it — so
    # paraphrases could never be learned from live traffic. Truncated rather
    # than stored whole: enough to recover the wording, bounded so the JSONL
    # doesn't grow without limit. Note this log now contains untrusted text.
    mediator_snippet:        Optional[str] = None
    sanitization_decision:   Optional[Dict[str, Any]] = None   # from 3C, if triggered
    permission_decision:     Optional[Dict[str, Any]] = None   # from Layer 4 Permission Control
    egress_decision:         Optional[Dict[str, Any]] = None   # from Layer 4 Egress Filter
    sandbox_result:           Optional[Dict[str, Any]] = None   # from Layer 4 Sandbox, if a command was executed
    outcome_severity:        int = 0        # 0=benign, 1=diagnostic, 2=high-impact
    final_status:            str = "unknown"  # blocked / approved_direct / approved_causal / safe_continuation
    timestamp:                str = field(default_factory=lambda: datetime.now().isoformat())


class TelemetryStream:
    def __init__(self, log_dir: str = "logs/episode_records"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "episodes.jsonl")
        self.buffer: List[EpisodeRecord] = []

    def emit(self, record: EpisodeRecord) -> None:
        self.buffer.append(record)
        with open(self.log_file, "a") as f:
            f.write(json.dumps(asdict(record)) + "\n")
        print(f"[TelemetryStream] Episode {record.boundary_index} logged — "
              f"status={record.final_status}, severity={record.outcome_severity}")

    def get_buffer(self) -> List[EpisodeRecord]:
        return self.buffer

    def load_all(self) -> List[Dict[str, Any]]:
        """Used later by the Adaptive Threat Model (3D) to load training data."""
        if not os.path.exists(self.log_file):
            return []
        with open(self.log_file, "r") as f:
            return [json.loads(line) for line in f if line.strip()]


if __name__ == "__main__":
    stream = TelemetryStream(log_dir="logs/episode_records")

    record = EpisodeRecord(
        boundary_index=1,
        tool_name="send_email",
        proposed_action="send_email to attacker@evil.com",
        causal_verdict={"ace": -0.5, "ie": 1.0, "de": 0.2, "takeover": True},
        sanitization_decision={"instructions_removed": ["ignore previous"], "facts_preserved": []},
        permission_decision={"allowed": True, "reason": "within scope"},
        egress_decision={"allowed": False, "reason": "destination not in allowlist"},
        outcome_severity=2,
        final_status="safe_continuation"
    )
    stream.emit(record)

    all_records = stream.load_all()
    print(f"\nTotal episodes on disk: {len(all_records)}")