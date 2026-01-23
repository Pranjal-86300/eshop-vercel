from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Payload(BaseModel):
    regions: list[str]
    threshold_ms: float

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "q-vercel-latency.json"
)

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/")
def latency(payload: Payload):
    with open(DATA_PATH) as f:
        data = json.load(f)

    result = {}

    for region in payload.regions:
        rows = [r for r in data if r["region"] == region]

        lat = np.array([r["latency_ms"] for r in rows])
        up = np.array([r["uptime_pct"] for r in rows])

        result[region] = {
            "avg_latency": float(lat.mean()),
            "p95_latency": float(np.percentile(lat, 95)),
            "avg_uptime": float(up.mean()),
            "breaches": int((lat > payload.threshold_ms).sum())
        }

    return result
