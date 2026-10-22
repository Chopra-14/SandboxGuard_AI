# e:/GPP/Task_40/Celesto_Sandboxes/agent/run.py
import subprocess
import json
import uuid
import logging
from pathlib import Path
import requests

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
API_URL = "http://localhost:8080/api/runs"
DOCKER_IMAGE = "python:3.11-slim"
SANDBOX_CMD = 'python -c "print(\'hello from sandbox\')"'

# ----------------------------------------------------------------------
# Logging setup
# ----------------------------------------------------------------------
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

run_id = str(uuid.uuid4())
log_file = log_dir / f"run_{run_id}.log"

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


# ----------------------------------------------------------------------
# Helper to run shell commands
# ----------------------------------------------------------------------
def exec_cmd(cmd: str):
    """Run a shell command, capture stdout/stderr, and log everything."""
    logging.info(f"Executing: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        logging.info(f"Return code: {result.returncode}")
        logging.info(f"stdout: {result.stdout.strip()}")
        logging.info(f"stderr: {result.stderr.strip()}")
        return result.returncode, result.stdout, result.stderr
    except Exception as exc:
        logging.exception(f"Exception while running command: {exc}")
        return 1, "", str(exc)


# ----------------------------------------------------------------------
# Main workflow
# ----------------------------------------------------------------------
def main():
    sandbox_name = f"sbx-{run_id[:8]}"  # short readable name

    # 1️⃣ Create (run) the sandbox container
    #    --rm makes Docker delete the container when it exits
    create_cmd = (
        f"docker run --name {sandbox_name} --rm -d {DOCKER_IMAGE} tail -f /dev/null"
    )
    rc, _, err = exec_cmd(create_cmd)
    if rc != 0:
        logging.error(f"Failed to start sandbox container: {err}")
        state = "failed"
        post_run(state, sandbox_name)
        return

    # 2️⃣ Execute the safe command inside the sandbox
    exec_cmd_str = f"docker exec {sandbox_name} {SANDBOX_CMD}"
    rc, out, err = exec_cmd(exec_cmd_str)
    state = "succeeded" if rc == 0 else "failed"

    # 3️⃣ Record the run in the API
    post_run(state, sandbox_name)

    # Log failure details if needed
    if state == "failed":
        # Append a line to failure_trace.jsonl
        trace_path = Path(__file__).parent.parent / "reports" / "failure_trace.jsonl"
        with open(trace_path, "a", encoding="utf-8") as tf:
            tf.write(json.dumps({"run_id": run_id, "policy_applied": "fresh", "state": state}) + "\n")
        logging.info(f"Failure trace written to {trace_path}")

    # 4️⃣ Cleanup – stop the container (it will be removed automatically)
    stop_cmd = f"docker stop {sandbox_name}"
    exec_cmd(stop_cmd)
    logging.info(f"Sandbox {sandbox_name} cleanup complete")


def post_run(state: str, sandbox_name: str):
    payload = {
        "run_id": run_id,
        "sandbox_name": sandbox_name,
        "problem_id": "demo",
        "state": state,
        "execution_target": "celesto_sandbox",
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
        resp.raise_for_status()
        logging.info(f"Run record posted successfully (status {resp.status_code})")
    except Exception as exc:
        logging.exception(f"Failed to post run record: {exc}")


if __name__ == "__main__":
    main()