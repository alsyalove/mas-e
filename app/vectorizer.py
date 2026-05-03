from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

MODEL_PATH = Path("models/vectorizer.pkl")
CORPUS_PATH = Path("data/reference_corpus.txt")


def load_corpus():
    if not CORPUS_PATH.exists():
        raise RuntimeError("Corpus tidak ditemukan")

    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        corpus = [line.strip() for line in f.readlines() if line.strip()]

    if not corpus:
        raise RuntimeError("Corpus kosong")

    return corpus


def get_vectorizer():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)

    corpus = load_corpus()

    vectorizer = TfidfVectorizer(
        # v2.2: max_features=20
        # v2.3: dinaikkan ke 100 untuk memberi ruang vektor yang lebih kaya
        # Diperlukan oleh Anchor Distance Calculation di Phase 2
        # RAM overhead minimal, tetap aman untuk VM 1GB
        max_features=100,
        sublinear_tf=True,   # baru: mengurangi dominasi term frekuensi tinggi
    )

    vectorizer.fit(corpus)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, MODEL_PATH)

    return vectorizer
