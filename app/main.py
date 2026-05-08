from datetime import datetime, timezone
from pathlib import Path
import json
import uuid

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.semantic_metrics import compute_metrics
from app.engine import evaluate_collapse, load_policy
from app.vectorizer import get_vectorizer
from app.anchor import get_anchor_vector, compute_anchor_distance, load_anchor
from app.drift_logger import build_drift_entry, log_drift

app = FastAPI()
vectorizer    = get_vectorizer()
anchor_vector = get_anchor_vector(vectorizer)

LOG_FILE = Path("logs/session.jsonl")
LOG_FILE.parent.mkdir(exist_ok=True)

NODE_ID = "cell-0"


class InputData(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


@app.get("/health")
def health():
    anchor = load_anchor()
    return {
        "status":        "alive",
        "node":          NODE_ID,
        "anchor":        anchor.get("anchor_id", "none"),
        "anchor_status": anchor.get("status", "unknown")
    }


@app.post("/process")
async def process_input(data: InputData):
    tfidf_vector = vectorizer.transform([data.text]).toarray()[0]

    if not np.any(tfidf_vector):
        return {
            "error": "Input tidak dikenali corpus",
            "hint":  "Gunakan kata yang ada di corpus referensi"
        }

    policy     = load_policy()
    motion_ref = policy.get("motion_ref", 0.022)

    anchor_distance      = None
    drift_entry          = None

    if anchor_vector is not None:
        distance    = compute_anchor_distance(tfidf_vector, anchor_vector)
        anchor      = load_anchor()
        alert       = distance > policy.get(
                          "anchor_thresholds", {}
                      ).get("drift_alert", 0.65)
        anchor_distance = distance
        drift_entry     = build_drift_entry(
            anchor_id            = anchor.get("anchor_id", "unknown"),
            distance_from_anchor = distance,
            alert                = alert
        )

    metrics    = compute_metrics(tfidf_vector, anchor_vector, motion_ref)
    decision   = evaluate_collapse(metrics, anchor_distance)
    session_id = str(uuid.uuid4())
    timestamp  = datetime.now(timezone.utc).isoformat()

    if drift_entry is not None:
        log_drift(drift_entry, session_id, NODE_ID)

    response = {
        "node_id":    NODE_ID,
        "session_id": session_id,
        "input":      data.text,
        "metrics":    metrics,
        "decision":   decision,
        "drift":      drift_entry,
        "timestamp":  timestamp
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(response) + "\n")

    return response
