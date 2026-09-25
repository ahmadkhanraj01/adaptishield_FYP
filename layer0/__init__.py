import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Tuple, List, Optional

@dataclass
class ServerRecord:
    name: str
    url: str
    tool_capabilities: List[str]
    version: str
    registered_at: str
    signature: str

class ServerTrustRegistry:
    def __init__(self):
        self.registry: Dict[str, ServerRecord] = {}

    def _compute_signature(self, name: str, url: str,
                           version: str, capabilities: List[str]) -> str:
        content = f"{name}{url}{version}{sorted(capabilities)}"
        return hashlib.sha256(content.encode()).hexdigest()

    def register_server(self, name: str, url: str,
                        version: str, capabilities: List[str]) -> str:
        sig = self._compute_signature(name, url, version, capabilities)
        record = ServerRecord(
            name=name,
            url=url,
            tool_capabilities=capabilities,
            version=version,
            registered_at=datetime.now().isoformat(),
            signature=sig
        )
        self.registry[name] = record
        print(f"[Registry] Registered: {name} v{version}")
        return sig

    def verify_server(self, name: str, url: str,
                      version: str, capabilities: List[str]) -> Tuple[bool, str]:
        if name not in self.registry:
            return False, "Server not registered"
        record = self.registry[name]
        current_sig = self._compute_signature(name, url, version, capabilities)
        if current_sig != record.signature:
            return False, "RUG-PULL DETECTED: signature mismatch"
        return True, "Verified"

    def get_allowlist(self) -> List[str]:
        return [r.url for r in self.registry.values()]


if __name__ == "__main__":
    registry = ServerTrustRegistry()

    # Register a server
    registry.register_server(
        "weather-api", "https://api.weather.com",
        "1.0", ["get_weather"]
    )

    # Legitimate verification
    ok, msg = registry.verify_server(
        "weather-api", "https://api.weather.com",
        "1.0", ["get_weather"]
    )
    print(f"Legitimate check: {ok} — {msg}")

    # Simulate rug-pull attack
    ok, msg = registry.verify_server(
        "weather-api", "https://api.weather.com",
        "1.1", ["get_weather", "exfiltrate_data"]
    )
    print(f"Rug-pull check: {ok} — {msg}")