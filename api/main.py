import os
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Literal, List
import sqlalchemy
from sqlalchemy import create_engine, Table, Column, String, MetaData
from sqlalchemy.sql import select, insert

# Load environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
API_PORT = int(os.getenv("API_PORT", "8080"))

engine = create_engine(DATABASE_URL, echo=False, future=True)
metadata = MetaData()

# Define runs table (id column optional, using run_id as primary key)
runs_table = Table(
    "runs",
    metadata,
    Column("run_id", String, primary_key=True),
    Column("sandbox_name", String, nullable=False),
    Column("problem_id", String, nullable=False),
    Column("state", String, nullable=False),
    Column("execution_target", String, nullable=False),
)

# Ensure table exists (creates if not)
metadata.create_all(engine)

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

class RunIn(BaseModel):
    run_id: str = Field(..., min_length=1)
    sandbox_name: str = Field(..., pattern="^sbx-[a-z0-9]{8,}$")
    problem_id: str = Field(..., min_length=1)
    state: Literal["created", "ready", "running", "succeeded", "failed", "deleted"]
    execution_target: Literal["celesto_sandbox"]

    @validator("execution_target")
    def check_target(cls, v):
        if v != "celesto_sandbox":
            raise ValueError("execution_target must be celesto_sandbox")
        return v

@app.get("/api/runs")
async def list_runs():
    with engine.connect() as conn:
        result = conn.execute(select(runs_table)).mappings()
        rows = [dict(row) for row in result]
    return JSONResponse(content=rows)

@app.post("/api/runs", status_code=status.HTTP_201_CREATED)
async def create_run(run: RunIn):
    # Insert into DB, handling duplicate primary key error
    with engine.begin() as conn:
        try:
            conn.execute(insert(runs_table).values(**run.dict()))
        except sqlalchemy.exc.IntegrityError:
            raise HTTPException(status_code=400, detail="run_id already exists")
    return run
