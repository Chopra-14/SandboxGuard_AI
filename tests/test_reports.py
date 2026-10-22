import json
import pathlib
import requests
import pytest

BASE_URL = "http://localhost:8080"
REPORTS_DIR = pathlib.Path(__file__).parent.parent / "reports"

def test_api_health():
    """Check the FastAPI health endpoint returns status ok."""
    resp = requests.get(f"{BASE_URL}/health")
    assert resp.status_code == 200, f"Health endpoint returned {resp.status_code}"
    data = resp.json()
    assert data.get("status") == "ok", "Health response does not contain status='ok'"

@pytest.mark.parametrize("filename", [p.name for p in REPORTS_DIR.iterdir() if p.suffix == ".json"])
def test_report_json_is_valid(filename):
    """Each report JSON file should be parseable and contain at least one key."""
    path = REPORTS_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        assert content.strip(), f"Report {filename} is empty"
        data = json.loads(content)
        assert isinstance(data, dict), f"Report {filename} is not a JSON object"
        assert data, f"Report {filename} contains no keys"
