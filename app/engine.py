from pathlib import Path
import yaml

THRESHOLD_PATH = Path("rules/thresholds.yaml")
_policy_cache = None


def load_policy() -> dict:
    global _policy_cache
    if _policy_cache is not None:
        return _policy_cache
    if not THRESHOLD_PATH.exists():
        raise RuntimeError(f"Threshold policy tidak ditemukan: {THRESHOLD_PATH}")
    with open(THRESHOLD_PATH, "r", encoding="utf-8") as f:
        _policy_cache = yaml.safe_load(f)
    return _policy_cache


def evaluate_collapse(
    metrics: dict,
    anchor_distance: float | None = None
) -> dict:
    policy        = load_policy()
    thresholds    = policy["collapse_thresholds"]
    anchor_thresh = policy.get("anchor_thresholds", {})
    lifecycle_map = policy["lifecycle_map"]
    seal_map      = policy["seal_map"]

    axes      = metrics["axes"]
    clarity   = axes["clarity_ambiguity"]
    motion    = axes["stillness_motion"]
    magnitude = metrics["magnitude"]

    dominant_axis = max(axes.items(), key=lambda x: abs(x[1]))[0]

    # 0. Drift override — input terlalu jauh dari anchor
    if (anchor_distance is not None
            and anchor_distance > anchor_thresh.get("drift_override", 0.85)):
        state  = "HOLD"
        glyph  = "clarity_ambiguity"
        reason = f"Input terlalu jauh dari anchor (distance: {anchor_distance:.3f})"

    # 1. Magnitude — sinyal belum cukup
    elif magnitude < thresholds["magnitude_observe"]:
        state  = "OBSERVE"
        glyph  = "origin"
        reason = "Sinyal belum cukup — dekat titik permulaan"

    # 2. Cipher — clarity sangat negatif
    elif clarity < thresholds["clarity_cipher"]:
        state  = "HOLD"
        glyph  = "clarity_ambiguity"
        reason = "Ambiguitas dominan — cipher belum terpecahkan"

    # 3. Paradox — gerak potensial
    elif motion < thresholds["motion_paradox"]:
        state  = "POTENTIAL"
        glyph  = "stillness_motion"
        reason = "Gerak potensial terdeteksi — makna bergerak ke dalam"

    # 4. Ascend — clarity cukup (anchor alignment kuat)
    elif clarity > thresholds["clarity_ascend"]:
        state  = "COLLAPSE"
        glyph  = "pure_knowledge"
        reason = "Makna selaras dengan anchor — collapse terjadi"

    # 5. Default
    else:
        state  = "OBSERVE"
        glyph  = "humility"
        reason = "Paradox aktif — belum cukup jelas untuk collapse"

    return {
        "state":           state,
        "seal":            seal_map.get(state, "reflection"),
        "glyph":           glyph,
        "reason":          reason,
        "dominant_axis":   dominant_axis,
        "lifecycle_phase": lifecycle_map.get(state, "unknown"),
    }
