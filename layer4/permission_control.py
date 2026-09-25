from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class PermissionDecision:
    server_name:     str
    requested_scope: str
    allowed:         bool
    reason:          str
    timestamp:       str


class PermissionControl:
    def __init__(self, registry=None):
        # registry: ServerTrustRegistry instance — queried for capability scope
        self.registry = registry
        self.violation_log: List[PermissionDecision] = []

    def check_scope(self, server_name: str, requested_capability: str) -> PermissionDecision:
        if self.registry is None or server_name not in self.registry.registry:
            decision = PermissionDecision(
                server_name=server_name,
                requested_scope=requested_capability,
                allowed=False,
                reason=f"Server '{server_name}' not found in Server Trust Registry",
                timestamp=datetime.now().isoformat()
            )
            self.violation_log.append(decision)
            print(f"[PermissionControl] {decision.reason}")
            return decision

        record = self.registry.registry[server_name]
        allowed = requested_capability in record.tool_capabilities

        reason = (
            f"'{requested_capability}' is within declared scope for {server_name}"
            if allowed else
            f"OUT-OF-SCOPE: '{requested_capability}' not declared for {server_name} "
            f"(declared: {record.tool_capabilities})"
        )

        decision = PermissionDecision(
            server_name=server_name,
            requested_scope=requested_capability,
            allowed=allowed,
            reason=reason,
            timestamp=datetime.now().isoformat()
        )

        if not allowed:
            self.violation_log.append(decision)
            print(f"[PermissionControl] {decision.reason}")

        return decision

    def get_violations(self) -> List[PermissionDecision]:
        return self.violation_log


if __name__ == "__main__":
    from layer0.server_trust_registry import ServerTrustRegistry

    registry = ServerTrustRegistry()
    registry.register_server(
        "weather-api", "https://api.weather.com",
        "1.0", ["get_weather"]
    )

    pc = PermissionControl(registry=registry)

    ok = pc.check_scope("weather-api", "get_weather")
    print(f"In-scope request: allowed={ok.allowed}")

    bad = pc.check_scope("weather-api", "delete_file")
    print(f"Out-of-scope request: allowed={bad.allowed}")

    unknown = pc.check_scope("unregistered-server", "anything")
    print(f"Unregistered server: allowed={unknown.allowed}")

    print(f"\nViolations logged: {len(pc.get_violations())}")