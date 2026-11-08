
from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    AskRequest,
    AskResponse,
    SearchRequest,
    SearchResponse,
    HealthResponse,
    DocumentsResponse,
    IngestRequest,
    IngestResponse
)

from app.rag_pipeline import RAGPipeline
from app.retrieval.search_engine import SearchEngine
from app.retrieval.vector_store import VectorStore
from app.ingestion.indexer import index_chunks

import json
from pathlib import Path


router = APIRouter(prefix="/api", tags=["Assistant Scolarité"])


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"


# Cache des pipelines pour éviter de recharger
# le modèle d'embeddings à chaque question.
pipelines = {}


def get_pipeline(strategy: str):
    if strategy not in pipelines:
        pipelines[strategy] = RAGPipeline(strategy=strategy)

    return pipelines[strategy]


# =====================================
# 1. HEALTH
# =====================================

@router.get("/health", response_model=HealthResponse)
def health():

    return {
        "status": "ok",
        "message": "Assistant Scolarité EIH est opérationnel."
    }


# =====================================
# 2. ASK
# =====================================

@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):

    try:
        pipeline = get_pipeline(request.strategy)

        result = pipeline.ask(
            question=request.question,
            top_k=request.top_k
        )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération : {str(error)}"
        )


# =====================================
# 3. SEARCH
# =====================================

@router.post("/search", response_model=SearchResponse)
def search_documents(request: SearchRequest):

    try:
        engine = SearchEngine(request.strategy)

        results = engine.search(
            question=request.question,
            top_k=request.top_k
        )

        # Filtrage optionnel par type de document
        if request.document_type:
            results = [
                result for result in results
                if result.get("document_type") == request.document_type
            ]

        return {
            "question": request.question,
            "results": results,
            "total": len(results),
            "strategy": request.strategy
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recherche : {str(error)}"
        )


# =====================================
# 4. INGEST
# =====================================

@router.post("/ingest", response_model=IngestResponse)
def ingest_documents(request: IngestRequest):

    try:
        index_chunks(strategy=request.strategy)

        store = VectorStore(strategy=request.strategy)
        count = store.count()

        # Vider le cache pour utiliser les nouveaux index
        pipelines.pop(request.strategy, None)

        return {
            "status": "success",
            "message": "Indexation terminée avec succès.",
            "strategy": request.strategy,
            "indexed_chunks": count
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'indexation : {str(error)}"
        )


# =====================================
# 5. DOCUMENTS
# =====================================

@router.get("/documents", response_model=DocumentsResponse)
def get_documents():

    documents = {}

    for strategy in ["fixed", "structural"]:

        chunks_file = CHUNKS_DIR / f"chunks_{strategy}.json"

        if not chunks_file.exists():
            continue

        with open(chunks_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        for chunk in data.get("chunks", []):

            filename = chunk.get("file")

            if filename not in documents:

                documents[filename] = {
                    "filename": filename,
                    "reference": chunk.get("reference"),
                    "document_type": chunk.get("type"),
                    "date": chunk.get("date"),
                    "version": chunk.get("version")
                }

    return {
        "total": len(documents),
        "documents": list(documents.values())
    }
