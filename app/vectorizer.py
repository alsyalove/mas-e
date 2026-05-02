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
        max_features=20
    )

    vectorizer.fit(corpus)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, MODEL_PATH)

    return vectorizer
