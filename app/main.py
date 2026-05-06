from datetime import datetime, timezone
from pathlib import Path
import json
import uuid

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.semantic_metrics import compute_metrics
from app.engine import evaluate_collapse
from app.vectorizer import get_vectorizer

app = FastAPI()
vectorizer = get_vectorizer()

LOG_FILE = Path("logs/session.jsonl")
LOG_FILE.parent.mkdir(exist_ok=True)   # cukup sekali saat startup

# Node identity — akan berkembang menjadi multi-node di Phase 3
NODE_ID = "cell-0"


class InputData(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


@app.get("/health")
def health():
    return {"status": "alive", "node": NODE_ID}


@app.post("/process")
async def process_input(data: InputData):
    tfidf_vector = vectorizer.transform([data.text]).toarray()[0]

    if not np.any(tfidf_vector):
        return {
            "error": "Input tidak dikenali corpus",
            "hint":  "Gunakan kata yang ada di corpus referensi"
        }

    metrics  = compute_metrics(tfidf_vector)
    decision = evaluate_collapse(metrics)

    response = {
        # --- Identity (v2.3) ---
        "node_id":    NODE_ID,
        "session_id": str(uuid.uuid4()),

        # --- Core ---
        "input":    data.text,
        "metrics":  metrics,
        "decision": decision,

        # --- Drift placeholder (kompatibel dengan Phase 2) ---
        # Akan berkembang menjadi:
        # { "distance_from_anchor": 0.41, "drift_speed": 0.08, "drift_angle": 31.5 }
        "drift": None,

        # --- Timestamp ---
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(response) + "\n")

    return response
