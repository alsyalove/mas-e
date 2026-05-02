import numpy as np

def compute_metrics(text_vector):
    variance = np.var(text_vector)
    mean = np.mean(text_vector)

    ambiguity = 1 / (1 + abs(mean))
    coherence = max(0.0, 1 - variance)

    return {
        "ambiguity": float(ambiguity),
        "coherence": float(coherence),
        "variance": float(variance),
        "mean": float(mean)
    }
