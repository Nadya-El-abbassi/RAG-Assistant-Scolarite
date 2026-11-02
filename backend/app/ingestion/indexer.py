
from pathlib import Path
import json

from app.retrieval.embedding_model import EmbeddingModel
from app.retrieval.vector_store import VectorStore


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"


def index_chunks(strategy: str = "fixed"):

    if strategy not in ("fixed", "structural"):
        raise ValueError("Stratégie invalide")

    chunks_file = CHUNKS_DIR / f"chunks_{strategy}.json"

    if not chunks_file.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {chunks_file}"
        )

    # 1. Charger les chunks
    with open(
        chunks_file,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    chunks = data["chunks"]

    if not chunks:
        raise ValueError("Aucun chunk à indexer")

    print("Nombre de chunks :", len(chunks))

    # 2. Charger le modèle
    embedding_model = EmbeddingModel()

    # 3. Transformer les textes en vecteurs
    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = embedding_model.encode(texts)

    print("Embeddings générés :", embeddings.shape)

    # 4. Initialiser ChromaDB
    vector_store = VectorStore(strategy)

    # 5. Réinitialiser la collection pour
    # reconstruire intégralement l'index
    vector_store.reset_collection()

    # 6. Enregistrer les chunks et vecteurs
    vector_store.add_chunks(
        chunks=chunks,
        embeddings=embeddings
    )

    print("\n================================")
    print("INDEXATION TERMINEE")
    print("Stratégie :", strategy)
    print("Collection :", vector_store.collection_name)
    print("Fragments indexés :", vector_store.count())
    print("================================")


if __name__ == "__main__":

    index_chunks(strategy="fixed")
