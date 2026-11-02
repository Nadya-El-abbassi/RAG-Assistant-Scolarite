
from pathlib import Path
import chromadb

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"


class VectorStore:

    def __init__(self, strategy: str = "fixed"):

        CHROMA_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        self.collection_name = f"eih_{strategy}"

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def reset_collection(self):

        self.client.delete_collection(
            name=self.collection_name
        )

        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(
        self,
        chunks: list[dict],
        embeddings
    ):

        if not chunks:
            return

        batch_size = 100

        for start in range(0, len(chunks), batch_size):

            batch = chunks[start:start + batch_size]

            batch_embeddings = embeddings[
                start:start + batch_size
            ]

            ids = []
            documents = []
            metadatas = []

            for chunk in batch:

                ids.append(chunk["id"])

                documents.append(chunk["text"])

                # Chroma n'accepte pas les valeurs None
                metadata = {
                    key: value
                    for key, value in chunk.items()
                    if key not in ("id", "chunk_id", "text")
                    and value is not None
                    and isinstance(value, (str, int, float, bool))
                }

                metadatas.append(metadata)

            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=batch_embeddings.tolist(),
                metadatas=metadatas
            )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict | None = None
    ):

        if top_k < 1:
            raise ValueError("top_k doit être supérieur à 0")

        if self.collection.count() == 0:
            return []

        where = None

        if filters:
            where = {
                key: value
                for key, value in filters.items()
                if value is not None
            }

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count()),
            where=where
        )

        output = []

        for i in range(len(results["ids"][0])):

            distance = results["distances"][0][i]

            output.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": distance,
                "score": 1 - distance
            })

        return output

    def count(self):

        return self.collection.count()
