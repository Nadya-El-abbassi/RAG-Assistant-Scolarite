
from app.retrieval.embedding_model import EmbeddingModel
from app.retrieval.vector_store import VectorStore


class SearchEngine:
    def __init__(self, strategy: str = "fixed"):
        if strategy not in ("fixed", "structural"):
            raise ValueError("La stratégie doit être 'fixed' ou 'structural'.")

        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore(strategy=strategy)

    def search(
        self,
        question: str,
        top_k: int = 5,
        doc_type: str | None = None
    ) -> list[dict]:

        if not question.strip():
            raise ValueError("La question ne peut pas être vide.")

        if top_k < 1:
            raise ValueError("top_k doit être supérieur ou égal à 1.")

        # 1. Transformer la question en embedding
        query_embedding = self.embedding_model.encode_query(question)

        # 2. Préparer le filtre éventuel
        filters = None
        if doc_type:
            filters = {"type": doc_type}

        # 3. Rechercher les chunks dans ChromaDB
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters
        )

        # 4. Organiser les résultats
        formatted_results = []

        for rank, result in enumerate(results, start=1):
            metadata = result["metadata"]

            formatted_results.append({
                "rank": rank,
                "chunk_id": result["id"],
                "content": result["text"],
                "score": round(result["score"], 4),
                "distance": round(result["distance"], 4),
                "source": metadata.get("file"),
                "reference": metadata.get("reference"),
                "document_type": metadata.get("type"),
                "page": metadata.get("page"),
                "section": metadata.get("section"),
                "date": metadata.get("date"),
                "version": metadata.get("version")
            })

        return formatted_results


if __name__ == "__main__":
    engine = SearchEngine(strategy="fixed")

    question = "Quelle est la durée minimale du stage PFE ?"

    results = engine.search(question, top_k=5)

    print(f"\nQuestion : {question}")
    print(f"Nombre de résultats : {len(results)}")

    for result in results:
        print("\n" + "=" * 60)
        print(f"Rang : {result['rank']}")
        print(f"Score : {result['score']}")
        print(f"Source : {result['source']}")
        print(f"Page : {result['page']}")
        print(f"Contenu :\n{result['content']}")
