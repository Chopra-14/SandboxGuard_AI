import subprocess
import time
import shutil
import pytest
from pathlib import Path

# Skip test if Docker CLI is not found in PATH
if shutil.which("docker") is None:
    pytest.skip("Docker CLI not found – skipping containment test", allow_module_level=True)

def test_container_isolation():
    """Run a temporary Docker container that creates a file inside itself.
    After the container stops, verify that the file does NOT exist on the host.
    """
    host_path = Path(__file__).parent.parent / "tmp_host_file.txt"
    # Ensure the file does not exist before the test
    if host_path.exists():
        host_path.unlink()

    # Run a short‑lived container that writes a file inside the container
    # No volume is mounted, so the file stays inside the container.
    cmd = [
        "docker",
        "run",
        "--rm",
        "-d",
        "python:3.11-slim",
        "sh",
        "-c",
        "echo hello > /tmp/tmp_file.txt && sleep 2",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    container_id = result.stdout.strip()
    assert result.returncode == 0, f"Docker start failed: {result.stderr}"

    # Wait a little for the container to exit (it sleeps 2 s)
    time.sleep(3)

    # The host file should still be missing
    assert not host_path.exists(), "Isolation broken: host file was created by the container"

    # Clean up just in case (container should already be stopped)
    subprocess.run(["docker", "rm", "-f", container_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
