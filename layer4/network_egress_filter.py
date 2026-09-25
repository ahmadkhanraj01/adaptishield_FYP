from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse


@dataclass
class EgressDecision:
    destination:    str
    allowed:        bool
    reason:         str
    timestamp:      str


class NetworkEgressFilter:
    def __init__(self, allowlist: Optional[List[str]] = None):
        # allowlist entries are full URLs or hostnames, e.g. "https://api.weather.com"
        self.allowlist = set(self._normalize(u) for u in (allowlist or []))
        self.blocked_log: List[EgressDecision] = []

    def _normalize(self, url: str) -> str:
        """Reduce a URL to just its hostname for comparison."""
        parsed = urlparse(url if "://" in url else f"https://{url}")
        return parsed.hostname or url

    def update_allowlist(self, urls: List[str]) -> None:
        """Called after ServerTrustRegistry registers/updates a server."""
        self.allowlist = set(self._normalize(u) for u in urls)
        print(f"[NetworkEgressFilter] Allowlist updated — {len(self.allowlist)} host(s)")

    def check(self, destination_url: str) -> EgressDecision:
        host = self._normalize(destination_url)
        allowed = host in self.allowlist
        reason = (
            "Destination host in registry allowlist" if allowed
            else f"BLOCKED: host '{host}' not in Server Trust Registry allowlist — potential exfiltration"
        )
        decision = EgressDecision(
            destination=destination_url,
            allowed=allowed,
            reason=reason,
            timestamp=datetime.now().isoformat()
        )
        if not allowed:
            self.blocked_log.append(decision)
            print(f"[NetworkEgressFilter] {decision.reason}")
        return decision

    def get_blocked_events(self) -> List[EgressDecision]:
        return self.blocked_log


if __name__ == "__main__":
    from layer0.server_trust_registry import ServerTrustRegistry

    registry = ServerTrustRegistry()
    registry.register_server(
        "weather-api", "https://api.weather.com",
        "1.0", ["get_weather"]
    )

    filt = NetworkEgressFilter(allowlist=registry.get_allowlist())

    ok = filt.check("https://api.weather.com/v1/forecast")
    print(f"Legitimate destination: allowed={ok.allowed}")

    bad = filt.check("https://attacker-c2.evil.com/exfil")
    print(f"Malicious destination: allowed={bad.allowed}")

    print(f"\nBlocked events logged: {len(filt.get_blocked_events())}")