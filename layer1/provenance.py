from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple


class ProvenanceLabel(Enum):
    USER_ORIGINATED = "user-originated"
    TOOL_RETURNED   = "tool-returned"
    MEMORY_RETRIEVED = "memory-retrieved"
    SYSTEM_GENERATED = "system-generated"


@dataclass
class ProvenanceSegment:
    content: str
    label: ProvenanceLabel
    source: str
    timestamp: str
    risk_flagged: bool = False


class InputParser:
    def parse_user_input(self, raw_input: str,
                         session_id: str) -> ProvenanceSegment:
        return ProvenanceSegment(
            content=raw_input,
            label=ProvenanceLabel.USER_ORIGINATED,
            source=f"user:{session_id}",
            timestamp=datetime.now().isoformat()
        )

    def parse_tool_response(self, response: str, tool_name: str,
                            risk_flagged: bool = False) -> ProvenanceSegment:
        return ProvenanceSegment(
            content=response,
            label=ProvenanceLabel.TOOL_RETURNED,
            source=f"tool:{tool_name}",
            timestamp=datetime.now().isoformat(),
            risk_flagged=risk_flagged
        )


class ContextBuilder:
    def __init__(self):
        self.trusted_prefix: List[ProvenanceSegment] = []
        self.mediator_view: List[ProvenanceSegment]  = []

    def reset(self) -> None:
        """Clears accumulated context. Call at the start of each
        independent request/boundary to prevent cross-request bleed."""
        self.trusted_prefix.clear()
        self.mediator_view.clear()

    def add_segment(self, segment: ProvenanceSegment) -> None:
        if segment.label == ProvenanceLabel.USER_ORIGINATED:
            self.trusted_prefix.append(segment)
        else:
            self.mediator_view.append(segment)

    def get_text_context(self) -> Tuple[str, str]:
        trusted  = "\n".join(s.content for s in self.trusted_prefix)
        mediator = "\n".join(s.content for s in self.mediator_view)
        return trusted, mediator

if __name__ == "__main__":
    parser  = InputParser()
    builder = ContextBuilder()

    user_seg = parser.parse_user_input("Summarise today's weather", "s1")
    tool_seg = parser.parse_tool_response("Temp: 25C, Clear", "weather_tool")

    builder.add_segment(user_seg)
    builder.add_segment(tool_seg)

    trusted, mediator = builder.get_text_context()
    print(f"Trusted prefix : {trusted}")
    print(f"Mediator view  : {mediator}")