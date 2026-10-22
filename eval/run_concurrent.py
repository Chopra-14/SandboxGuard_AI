import subprocess
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "http://localhost:8080/api/runs"

def run_agent_instance(idx):
    # Run the agent script; returns run_id and state
    proc = subprocess.run(["python", "agent/run.py"], capture_output=True, text=True)
    # Fetch latest run from API (assuming this run is the latest)
    resp = subprocess.run(["curl", "-s", API_URL], capture_output=True, text=True)
    try:
        data = json.loads(resp.stdout)
        latest = data[-1] if data else {}
        return {"index": idx, "run_id": latest.get("run_id"), "state": latest.get("state"), "sandbox_name": latest.get("sandbox_name")}
    except Exception:
        return {"index": idx, "error": "fetch_failed"}

def main():
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(run_agent_instance, i): i for i in range(5)}
        for future in as_completed(futures):
            results.append(future.result())
    # Write concurrency report
    reports_dir = Path(__file__).parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "concurrency.json").write_text(json.dumps({"concurrent_runs": results}, indent=2))
    print("Concurrency report written to reports/concurrency.json")

if __name__ == "__main__":
    main()
