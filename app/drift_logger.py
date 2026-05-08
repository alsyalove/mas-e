from pathlib import Path
import json
from datetime import datetime, timezone

DRIFT_LOG = Path("drift/drift.jsonl")


def build_drift_entry(
    anchor_id: str,
    distance_from_anchor: float,
    alert: bool
) -> dict:
    return {
        "anchor_id":            anchor_id,
        "distance_from_anchor": round(distance_from_anchor, 4),
        "alert":                alert,
        "drift_speed":          None,
        "drift_angle":          None,
        "trajectory":           None,
    }


def log_drift(drift_entry: dict, session_id: str, node_id: str) -> None:
    DRIFT_LOG.parent.mkdir(exist_ok=True)
    record = {
        "session_id": session_id,
        "node_id":    node_id,
        "drift":      drift_entry,
        "timestamp":  datetime.now(timezone.utc).isoformat()
    }
    with open(DRIFT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
