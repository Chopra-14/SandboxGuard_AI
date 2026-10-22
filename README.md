# Celesto Sandbox Agent

This repository contains a minimal **Celesto sandbox agent** implementation used for the hackathon.

## Project layout
```
Celesto_Sandboxes/
│   README.md                 # <-- you are here
│   requirements.txt
│
├───agent
│   ├── run.py                # sandbox driver script
│   └── logs/                 # per‑run logs (run_<run_id>.log)
│
├───api
│   └── main.py                # FastAPI service (exposes /health and /api/runs)
│
├───eval
│   ├── generate_reliability.py   # 20‑run reliability script
│   └── run_concurrent.py         # concurrency runner (5 parallel sandboxes)
│
├───reports
│   ├── problem.json
│   ├── capabilities.json
│   ├── lifecycle.json
│   ├── containment.json
│   └── failure_policy.json
│
└───tests
    ├── containment_test.py   # verifies sandbox isolation
    └── test_reports.py       # validates generated reports & API health
```

## Prerequisites
* **Windows PowerShell** (the repository assumes a Windows workstation).
* **Docker Desktop** – the ledger (Postgres) and API containers are defined in `docker-compose.yml`.
* **Python 3.11** (or later) with the packages listed in `requirements.txt`.

## Quick‑start
```powershell
# 1️⃣ Bring up the Docker stack (ledger + API)
cd e:/GPP/Task_40/Celesto_Sandboxes
docker compose up -d --force-recreate

# Verify the API health endpoint
curl http://localhost:8080/health
# Expected output: {"status":"ok"}

# 2️⃣ Run a single sandbox execution
python agent/run.py

# 3️⃣ List recorded runs
curl http://localhost:8080/api/runs
```
A successful run will have `"state":"succeeded"` and a corresponding log file under `agent/logs/`.

## Generating extra reports
```powershell
# Reliability (20 sequential runs)
python eval/generate_reliability.py

# Concurrency (5 parallel sandboxes)
python eval/run_concurrent.py
```
These scripts produce `reports/reliability.json`, `reports/concurrency.json` and a post‑mortem markdown file.

## Test suite
The repository ships with a pytest suite that checks two things:
1. **Containment** – a destructive command inside the Docker sandbox cannot affect the host filesystem.
2. **Report validation** – all JSON files under `reports/` adhere to the expected schema and the API health endpoint is reachable.

Run the full test suite with:
```powershell
pytest tests/
```
All tests should pass (`.` for each test).

## Cleanup
The sandbox driver (`agent/run.py`) automatically destroys the Docker container after the command finishes. If you need to stop the whole stack:
```powershell
docker compose down
```

---
*Feel free to explore the `eval/` scripts and adjust the `run.py` logic for more complex commands or different sandbox images.*