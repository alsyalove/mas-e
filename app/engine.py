from pathlib import Path
import yaml

THRESHOLD_PATH = Path("rules/thresholds.yaml")

# Cache agar tidak baca file setiap request
_policy_cache = None


def load_policy():
    global _policy_cache
    if _policy_cache is not None:
        return _policy_cache

    if not THRESHOLD_PATH.exists():
        raise RuntimeError(
            f"Threshold policy tidak ditemukan: {THRESHOLD_PATH}\n"
            "Pastikan rules/thresholds.yaml ada sebelum menjalankan sistem."
        )

    with open(THRESHOLD_PATH, "r", encoding="utf-8") as f:
        _policy_cache = yaml.safe_load(f)

    return _policy_cache


def evaluate_collapse(metrics):
    policy = load_policy()

    thresholds = policy["collapse_thresholds"]
    lifecycle_map = policy["lifecycle_map"]

    ambiguity = metrics["ambiguity"]
    coherence = metrics["coherence"]

    # --- Collapse Logic (tidak berubah dari v2.2) ---
    if ambiguity >= thresholds["ambiguity_hold"]:
        state = "HOLD"
        glyph = "clarity_ambiguity"
        reason = "Ambiguity terlalu tinggi"

    elif coherence >= thresholds["coherence_collapse"]:
        state = "COLLAPSE"
        glyph = "pure_knowledge"
        reason = "Distribusi relatif stabil"

    else:
        state = "OBSERVE"
        glyph = "humility"
        reason = "Belum cukup jelas"

    # --- Lifecycle Mapping (baru di v2.3) ---
    # Menerjemahkan collapse state ke Knowledge Lifecycle phase
    # Referensi: Volume I Bab V & rules/thresholds.yaml
    lifecycle_phase = lifecycle_map.get(state, "unknown")

    return {
        "state": state,
        "glyph": glyph,
        "reason": reason,
        "lifecycle_phase": lifecycle_phase,   # affordance untuk Phase 1
    }
