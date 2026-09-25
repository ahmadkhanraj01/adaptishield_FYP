import time
from dataclasses import dataclass
from typing import Optional, Dict, Any

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


@dataclass
class SandboxResult:
    success:      bool
    output:       str
    error:        str
    duration_sec: float
    container_id: Optional[str] = None


class Sandbox:
    """
    Docker-based process isolation for tool execution.
    Each tool call runs inside a short-lived, resource-limited container.

    Note: true gVisor (runsc) isolation requires the runsc runtime to be
    installed and configured as a Docker runtime (`--runtime=runsc`).
    This class supports that via `runtime="runsc"` once available on the
    host; it defaults to the standard Docker runtime for now.
    """

    def __init__(self, image: str = "python:3.10-slim",
                 runtime: Optional[str] = None,
                 mem_limit: str = "256m",
                 cpu_quota: int = 50000,   # 50% of one core
                 timeout_sec: int = 10):
        if not DOCKER_AVAILABLE:
            raise RuntimeError(
                "docker SDK not installed. Run: pip install docker"
            )
        self.client = docker.from_env()
        self.image = image
        self.runtime = runtime      # e.g. "runsc" for gVisor once configured
        self.mem_limit = mem_limit
        self.cpu_quota = cpu_quota
        self.timeout_sec = timeout_sec

    def run_tool(self, command: str, env: Optional[Dict[str, Any]] = None) -> SandboxResult:
        """
        Executes `command` inside an isolated container and returns the result.
        `command` should be a shell-executable string, e.g.
        'python3 -c "print(1+1)"'
        """
        start = time.time()
        container = None
        try:
            kwargs = dict(
                image=self.image,
                command=["sh", "-c", command],
                mem_limit=self.mem_limit,
                cpu_quota=self.cpu_quota,
                network_disabled=True,     # egress goes through NetworkEgressFilter, not raw container network
                environment=env or {},
                detach=True,
                remove=False,
            )
            if self.runtime:
                kwargs["runtime"] = self.runtime

            container = self.client.containers.run(**kwargs)
            exit_status = container.wait(timeout=self.timeout_sec)
            logs = container.logs(stdout=True, stderr=True).decode(errors="replace")
            duration = time.time() - start

            success = exit_status.get("StatusCode", 1) == 0
            print(f"[Sandbox] Container {container.short_id} finished "
                  f"({'ok' if success else 'error'}) in {duration:.2f}s")

            return SandboxResult(
                success=success,
                output=logs if success else "",
                error="" if success else logs,
                duration_sec=duration,
                container_id=container.short_id
            )
        except Exception as e:
            duration = time.time() - start
            print(f"[Sandbox] Execution failed: {e}")
            return SandboxResult(
                success=False,
                output="",
                error=str(e),
                duration_sec=duration,
                container_id=container.short_id if container else None
            )
        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception:
                    pass


if __name__ == "__main__":
    if not DOCKER_AVAILABLE:
        print("docker SDK not installed — run: pip install docker")
    else:
        sandbox = Sandbox()

        # Benign test
        r = sandbox.run_tool('python3 -c "print(2 + 2)"')
        print(f"\nBenign test — success={r.success}, output={r.output.strip()}")

        # Simulated failing/malicious command
        r = sandbox.run_tool('python3 -c "import sys; sys.exit(1)"')
        print(f"Failure test — success={r.success}, error={r.error.strip()}")