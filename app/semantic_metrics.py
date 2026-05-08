import numpy as np


def clamp(value: float) -> float:
    return max(-0.99, min(0.99, float(value)))


def compute_metrics(
    text_vector: np.ndarray,
    anchor_vector: np.ndarray | None = None,
    motion_ref: float = 0.022
) -> dict:
    active   = text_vector[text_vector > 0]
    n_active = int(len(active))

    mean     = float(np.mean(active)) if n_active > 0 else 0.0
    variance = float(np.var(active))  if n_active > 0 else 0.0
    density  = float(n_active / len(text_vector))

    if n_active == 0:
        return {
            "axes": {
                "clarity_ambiguity": 0.0,
                "stillness_motion":  0.0,
                "value_order":       0.0
            },
            "magnitude":       0.0,
            "active_features": 0,
            "raw": {"mean": 0.0, "variance": 0.0, "density": 0.0}
        }

    # Axis 1 — clarity_ambiguity (anchor-aware di Phase 1)
    if anchor_vector is not None and np.linalg.norm(anchor_vector) > 1e-10:
        norm_input  = np.linalg.norm(text_vector)
        norm_anchor = np.linalg.norm(anchor_vector)
        cos_sim     = float(np.dot(text_vector, anchor_vector)
                            / (norm_input * norm_anchor))
        cos_sim     = max(0.0, min(1.0, cos_sim))
        clarity_ambiguity = clamp(2 * cos_sim - 1)
    else:
        clarity_ambiguity = clamp(mean / (1 + abs(mean)))

    # Axis 2 — stillness_motion
    MOTION_REF        = max(motion_ref, 1e-10)
    normalized_motion = min(1.0, variance / MOTION_REF)
    stillness_motion  = clamp(2 * normalized_motion - 1)

    # Axis 3 — value_order
    if n_active == 1:
        value_order = 0.99
    else:
        p            = active / active.sum()
        entropy      = float(-np.sum(p * np.log(p + 1e-10)))
        max_entropy  = np.log(n_active)
        norm_entropy = entropy / max_entropy if max_entropy > 1e-10 else 0.0
        value_order  = clamp(1 - 2 * norm_entropy)

    magnitude = float(
        (clarity_ambiguity**2 + stillness_motion**2 + value_order**2) ** 0.5
    )

    return {
        "axes": {
            "clarity_ambiguity": round(clarity_ambiguity, 4),
            "stillness_motion":  round(stillness_motion, 4),
            "value_order":       round(value_order, 4)
        },
        "magnitude":       round(magnitude, 4),
        "active_features": n_active,
        "raw": {
            "mean":     round(mean, 4),
            "variance": round(variance, 4),
            "density":  round(density, 4)
        }
    }
