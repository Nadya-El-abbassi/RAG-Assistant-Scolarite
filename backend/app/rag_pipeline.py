
import re

from app.retrieval.search_engine import SearchEngine
from app.generation.prompt_builder import build_prompt
from app.generation.llm_client import LLMClient


# Seuil initial de similarité (à calibrer pendant l'évaluation)
SIMILARITY_THRESHOLD = 0.40

# Message officiel de refus
REFUSAL_MESSAGE = (
    "Je ne trouve pas cette information dans les documents de l'École."
)


def validate_citations(answer: str, number_of_sources: int) -> bool:
    """
    Vérifie que les citations utilisées dans la réponse
    correspondent aux numéros des sources disponibles.
    """

    citations = re.findall(r"\[(\d+)\]", answer)

    if not citations:
        return False

    for citation in citations:
        citation_number = int(citation)

        if citation_number < 1 or citation_number > number_of_sources:
            return False

    return True


class RAGPipeline:

    def __init__(self, strategy="structural"):

        if strategy not in ("fixed", "structural"):
            raise ValueError(
                "La stratégie doit être 'fixed' ou 'structural'."
            )

        self.strategy = strategy

        # Moteur de recherche
        self.search_engine = SearchEngine(strategy)

        # Client LLM
        self.llm = LLMClient()

    def ask(self, question: str, top_k: int = 5):

        if not question or not question.strip():
            raise ValueError("La question ne peut pas être vide.")

        if top_k < 1:
            raise ValueError("top_k doit être supérieur ou égal à 1.")

        # 1. Recherche des chunks pertinents
        results = self.search_engine.search(
            question,
            top_k=top_k
        )

        # 2. Filtrage par seuil de similarité
        results = [
            result for result in results
            if result["score"] >= SIMILARITY_THRESHOLD
        ]

        # 3. Refus si aucun résultat pertinent
        if not results:
            return {
                "question": question,
                "answer": REFUSAL_MESSAGE,
                "sources": [],
                "strategy": self.strategy
            }

        # 4. Construction du prompt
        prompts = build_prompt(question, results)

        # 5. Génération de la réponse
        answer = self.llm.generate(
            system_prompt=prompts["system"],
            user_prompt=prompts["user"]
        )

        # 6. Validation des citations
        citations_valides = validate_citations(
            answer,
            len(results)
        )

        if not citations_valides:
            answer = (
                "Je ne peux pas fournir une réponse suffisamment "
                "justifiée par les documents retrouvés."
            )

        # 7. Préparation des sources
        sources = []

        for index, result in enumerate(results, start=1):

            sources.append({
                "citation": f"[{index}]",
                "document": result.get("source"),
                "reference": result.get("reference"),
                "page": result.get("page"),
                "score": result.get("score")
            })

        # 8. Résultat final
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "strategy": self.strategy
        }


if __name__ == "__main__":

    question = "Quelle est la durée minimale du stage PFE ?"

    # Comparaison des deux stratégies
    for strategy in ["fixed", "structural"]:

        print("\n" + "=" * 60)
        print(f"STRATEGIE : {strategy.upper()}")
        print("=" * 60)

        rag = RAGPipeline(strategy=strategy)

        response = rag.ask(
            question=question,
            top_k=5
        )

        print("\nQUESTION :")
        print(response["question"])

        print("\nREPONSE :")
        print(response["answer"])

        print("\nSOURCES :")

        for source in response["sources"]:
            print(source)
