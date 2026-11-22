"""RAG retriever: job-description documents par TF-IDF search (no GPU / no API needed)."""
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from .config import DOCS_DIR


class Retriever:
    def __init__(self, docs_dir=DOCS_DIR):
        self.chunks = []          # [{"text":..., "source":...}]
        for f in sorted(Path(docs_dir).glob("*.txt")):
            for para in f.read_text(encoding="utf-8").split("\n\n"):
                para = para.strip()
                if len(para) > 30:
                    self.chunks.append({"text": para, "source": f.name})
        if self.chunks:
            self.vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self.matrix = self.vec.fit_transform([c["text"] for c in self.chunks])

    def search(self, query: str, k: int = 3):
        if not self.chunks:
            return []
        scores = linear_kernel(self.vec.transform([query]), self.matrix).ravel()
        top = scores.argsort()[::-1][:k]
        return [{**self.chunks[i], "score": round(float(scores[i]), 3)} for i in top if scores[i] > 0]
