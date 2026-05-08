from pathlib import Path
import yaml
import numpy as np

ANCHOR_PATH = Path("anchors/cell0_anchor.yaml")
_anchor_cache: dict | None = None


def load_anchor() -> dict:
    global _anchor_cache
    if _anchor_cache is not None:
        return _anchor_cache
    if not ANCHOR_PATH.exists():
        raise RuntimeError(f"Anchor schema tidak ditemukan: {ANCHOR_PATH}")
    with open(ANCHOR_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    _anchor_cache = data
    return _anchor_cache


def get_anchor_vector(vectorizer) -> np.ndarray | None:
    anchor = load_anchor()
    if anchor.get("status") != "active":
        return None
    terms = anchor.get("semantic_terms", [])
    if not terms:
        return None
    anchor_text = " ".join(terms)
    return vectorizer.transform([anchor_text]).toarray()[0]


def compute_anchor_distance(
    input_vector: np.ndarray,
    anchor_vector: np.ndarray
) -> float:
    norm_input  = np.linalg.norm(input_vector)
    norm_anchor = np.linalg.norm(anchor_vector)
    if norm_input < 1e-10 or norm_anchor < 1e-10:
        return 1.0
    cos_sim = float(
        np.dot(input_vector, anchor_vector) / (norm_input * norm_anchor)
    )
    cos_sim = max(0.0, min(1.0, cos_sim))
    return round(1.0 - cos_sim, 4)
