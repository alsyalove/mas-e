import numpy as np


def clamp(value: float) -> float:
    return max(-0.99, min(0.99, float(value)))


def compute_metrics(text_vector: np.ndarray) -> dict:
    """
    Hitung metrik semantik dari TF-IDF vector dalam ruang 3-axis bipolar.

    Semua axis dihitung dari active features saja (nilai > 0).
    TF-IDF vector bersifat sparse — menghitung dari seluruh vector
    termasuk nol menghasilkan metrik yang bias dan tidak bermakna.

    Tiga axis bipolar (range: -0.99 hingga 0.99):

    clarity_ambiguity
        positif → makna jelas, termanifestasi
        negatif → makna tersembunyi, potensial
        Catatan: dengan TF-IDF murni, axis ini selalu positif karena
        nilai TF-IDF tidak pernah negatif. Sisi negatif baru bermakna
        setelah Anchor aktif di Phase 1 (jarak dari anchor menghasilkan
        clarity relatif yang bisa negatif).

    stillness_motion
        positif → gerak kinetik: distribusi tidak merata, satu term dominan
        negatif → gerak potensial: distribusi merata, semua term seimbang
        Formula: dinormalisasi terhadap MOTION_REF (variance referensi max).

    value_order
        positif → terstruktur: entropy rendah, satu term dominan jelas
        negatif → chaos/noise: entropy tinggi, distribusi sangat merata
        Formula: berbasis entropy Shannon dari distribusi active features.
    """

    active = text_vector[text_vector > 0]
    n_active = int(len(active))

    # Raw stats
    mean     = float(np.mean(active)) if n_active > 0 else 0.0
    variance = float(np.var(active))  if n_active > 0 else 0.0
    density  = float(n_active / len(text_vector))

    # Guard: tidak ada fitur aktif
    # Seharusnya sudah ditangkap di main.py, tapi defensive
    if n_active == 0:
        return {
            "axes": {
                "clarity_ambiguity": 0.0,
                "stillness_motion":  0.0,
                "value_order":       0.0
            },
            "magnitude":      0.0,
            "active_features": 0,
            "raw": {
                "mean":     0.0,
                "variance": 0.0,
                "density":  0.0
            }
        }

    # ----------------------------------------------------------------
    # Axis 1 — clarity_ambiguity
    # ----------------------------------------------------------------
    # mean TF-IDF aktif selalu positif (0 < mean ≤ 1)
    # → axis ini selalu positif di Phase 0 (pre-anchor)
    # → rentang efektif saat ini: (0, 0.99)
    clarity_ambiguity = clamp(mean / (1 + abs(mean)))

    # ----------------------------------------------------------------
    # Axis 2 — stillness_motion
    # ----------------------------------------------------------------
    # variance aktif tinggi → distribusi tidak merata → satu term dominan → kinetik (+)
    # variance aktif rendah → distribusi merata → semua term seimbang → potensial (-)
    #
    # MOTION_REF: variance referensi empiris untuk TF-IDF dengan sublinear_tf=True.
    # Derivasi: active features dengan distribusi seragam dan sublinear_tf
    # menghasilkan variance maksimum sekitar 0.25.
    # Variance 0     → stillness_motion = -0.99 (full potential)
    # Variance 0.125 → stillness_motion =  0.0  (neutral)
    # Variance 0.25+ → stillness_motion = +0.99 (full kinetic)
    #
    # Konstanta ini AKAN perlu dikalibrasi ulang jika:
    #   - vectorizer diganti (bukan TF-IDF)
    #   - sublinear_tf dimatikan
    #   - corpus berkembang sangat besar dan distribusi berubah signifikan
    # Jika perlu dikalibrasi: jalankan baseline capture, amati variance raw
    # pada input yang beragam, set MOTION_REF = nilai variance tertinggi yang wajar.
    #
    # NOTE: Di Phase 1 — pertimbangkan migrasi ke thresholds.yaml
    #       jika corpus berkembang dan recalibration menjadi rutin.
    MOTION_REF = 0.25
    normalized_motion = min(1.0, variance / MOTION_REF)
    stillness_motion = clamp(2 * normalized_motion - 1)

    # ----------------------------------------------------------------
    # Axis 3 — value_order
    # ----------------------------------------------------------------
    # Entropy Shannon dari distribusi active features:
    # entropy rendah (satu term dominan) → order tinggi (+)
    # entropy tinggi (distribusi merata)  → chaos (-)
    if n_active == 1:
        # Satu fitur aktif = maximum order, tidak ada distribusi untuk dihitung
        value_order = 0.99
    else:
        p = active / active.sum()
        entropy = float(-np.sum(p * np.log(p + 1e-10)))
        max_entropy = np.log(n_active)           # entropy maksimum = log(n)
        normalized_entropy = (
            entropy / max_entropy if max_entropy > 1e-10 else 0.0
        )
        # normalized_entropy 0 → order = +0.99 (fully ordered)
        # normalized_entropy 0.5 → order = 0.0 (neutral)
        # normalized_entropy 1 → order = -0.99 (full chaos)
        value_order = clamp(1 - 2 * normalized_entropy)

    # ----------------------------------------------------------------
    # Magnitude — jarak dari titik permulaan dalam ruang 3D
    # ----------------------------------------------------------------
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
