from datetime import datetime, timezone
from pathlib import Path
import json

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.semantic_metrics import compute_metrics
from app.engine import evaluate_collapse
from app.vectorizer import get_vectorizer

app = FastAPI()
vectorizer = get_vectorizer()

LOG_FILE = Path("logs/session.jsonl")


class InputData(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


@app.get("/health")
def health():
    return {"status": "alive"}


@app.post("/process")
async def process_input(data: InputData):
    tfidf_vector = vectorizer.transform([data.text]).toarray()[0]

    if np.sum(tfidf_vector) == 0:
        return {
            "error": "Input tidak dikenali corpus",
            "hint": "Gunakan kata yang ada di corpus referensi"
        }

    metrics = compute_metrics(tfidf_vector)
    decision = evaluate_collapse(metrics)

    response = {
        "input": data.text,
        "metrics": metrics,
        "decision": decision,
        "drift": None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    LOG_FILE.parent.mkdir(exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(response) + "\n")

    return response
