from pathlib import Path
import yaml

THRESHOLD_PATH = Path("rules/thresholds.yaml")

# Cache agar tidak baca file setiap request
# Invalidate: restart service setelah mengubah thresholds.yaml
_policy_cache = None


def load_policy() -> dict:
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


def evaluate_collapse(metrics: dict) -> dict:
    """
    Evaluasi collapse state dari 3-axis bipolar metrics.

    Urutan evaluasi (tidak boleh dibalik):
    1. Magnitude  — apakah ada sinyal cukup?
    2. Cipher     — apakah clarity terlalu negatif?
    3. Paradox    — apakah ada gerak potensial?
    4. Ascend     — apakah clarity + order cukup kuat untuk collapse?
    5. Default    — observe, paradox aktif

    Semua threshold dibaca dari rules/thresholds.yaml.
    Tidak ada nilai numerik hardcoded di fungsi ini.
    """
    policy = load_policy()

    thresholds    = policy["collapse_thresholds"]
    lifecycle_map = policy["lifecycle_map"]
    seal_map      = policy["seal_map"]

    axes      = metrics["axes"]
    clarity   = axes["clarity_ambiguity"]
    motion    = axes["stillness_motion"]
    order     = axes["value_order"]
    magnitude = metrics["magnitude"]

    # Axis dengan nilai absolut terbesar
    dominant_axis = max(axes.items(), key=lambda x: abs(x[1]))[0]

    # ----------------------------------------------------------------
    # Collapse Logic
    # ----------------------------------------------------------------

    # 1. Terlalu dekat titik permulaan — belum cukup sinyal
    if magnitude < thresholds["magnitude_observe"]:
        state  = "OBSERVE"
        glyph  = "origin"
        reason = "Input berada dekat titik permulaan — sinyal belum cukup"

    # 2. Cipher — ambiguity dominan, makna tersembunyi
    elif clarity < thresholds["clarity_cipher"]:
        state  = "HOLD"
        glyph  = "clarity_ambiguity"
        reason = "Ambiguitas dominan — cipher belum terpecahkan"

    # 3. Paradox — gerak potensial terdeteksi
    elif motion < thresholds["motion_paradox"]:
        state  = "POTENTIAL"
        glyph  = "stillness_motion"
        reason = "Gerak potensial terdeteksi — makna bergerak ke dalam"

    # 4. Ascend — clarity dan order cukup kuat untuk collapse
    elif (clarity > thresholds["clarity_ascend"]
          and order > thresholds["order_ascend"]):
        state  = "COLLAPSE"
        glyph  = "pure_knowledge"
        reason = "Makna jelas dan terstruktur — collapse terjadi"

    # 5. Default — sinyal ada tapi belum cukup jelas
    else:
        state  = "OBSERVE"
        glyph  = "humility"
        reason = "Paradox aktif — belum cukup jelas untuk collapse"

    # ----------------------------------------------------------------
    # Seal & Lifecycle (dari policy, bukan hardcoded)
    # ----------------------------------------------------------------
    seal            = seal_map.get(state, "reflection")
    lifecycle_phase = lifecycle_map.get(state, "unknown")

    return {
        "state":           state,
        "seal":            seal,
        "glyph":           glyph,
        "reason":          reason,
        "dominant_axis":   dominant_axis,
        "lifecycle_phase": lifecycle_phase,   # affordance untuk Phase 1
    }
