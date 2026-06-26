import sys
sys.path.insert(0, ".")
from app.vectordb.factory import get_vectordb
from app.core.logger import logger

if __name__ == "__main__":
    db = get_vectordb()

    # Dummy embeddings (384 dims = all-MiniLM-L6-v2 output size)
    texts = ["The sky is blue.", "Python is a programming language.", "Voice agents are cool."]
    embeddings = [[0.1] * 384, [0.2] * 384, [0.3] * 384]
    metadatas = [{"source": "test"}] * 3

    db.add(texts, embeddings, metadatas)
    logger.success("Chunks stored!")

    results = db.search([0.1] * 384, top_k=2)
    for r in results:
        logger.info(f"score={r['score']:.3f} | {r['text']}")

    logger.success("Module 3 complete!")

