from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import List, Dict
import os

app = FastAPI()

# Enable CORS for any origin (POST)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load telemetry data (adjust path/filename as needed)

df = pd.read_json('q-vercel-latency.json')

@app.post("/api/metrics")
async def get_metrics(request: Request):
    body = await request.json()
    regions: List[str] = body.get("regions", [])
    threshold_ms: int = body.get("threshold_ms", 180)
    
    result = {}
    for region in regions:
        region_df = df[df["region"] == region]
        if region_df.empty:
            result[region] = {
                "avg_latency": 0.0,
                "p95_latency": 0.0,
                "avg_uptime": 0.0,
                "breaches": 0
            }
            continue
        
        latencies = region_df["latency_ms"].values
        uptimes = region_df["uptime"].values
        
        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = int(np.sum(latencies > threshold_ms))
        
        result[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 4),
            "breaches": breaches
        }
    
    return result
