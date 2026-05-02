def evaluate_collapse(metrics):
    ambiguity = metrics["ambiguity"]
    coherence = metrics["coherence"]

    if ambiguity >= 0.75:
        return {
            "state": "HOLD",
            "glyph": "clarity_ambiguity",
            "reason": "Ambiguity terlalu tinggi"
        }

    if coherence >= 0.65:
        return {
            "state": "COLLAPSE",
            "glyph": "pure_knowledge",
            "reason": "Distribusi relatif stabil"
        }

    return {
        "state": "OBSERVE",
        "glyph": "humility",
        "reason": "Belum cukup jelas"
    }
