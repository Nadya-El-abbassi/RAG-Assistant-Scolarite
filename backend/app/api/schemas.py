
from pydantic import BaseModel, Field
from typing import Literal


# =========================
# QUESTION / ASK
# =========================

class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question posée par l'étudiant"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Nombre de chunks à récupérer"
    )

    strategy: Literal["fixed", "structural"] = Field(
        default="structural",
        description="Stratégie de chunking utilisée"
    )


class SourceResponse(BaseModel):
    citation: str
    document: str | None = None
    reference: str | None = None
    page: int | None = None
    score: float | None = None


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceResponse]
    strategy: str


# =========================
# SEARCH
# =========================

class SearchRequest(BaseModel):
    question: str = Field(..., min_length=1)

    top_k: int = Field(
        default=5,
        ge=1,
        le=20
    )

    strategy: Literal["fixed", "structural"] = "structural"

    document_type: str | None = None


class SearchResult(BaseModel):
    rank: int
    chunk_id: str
    content: str
    score: float
    distance: float
    source: str | None = None
    reference: str | None = None
    document_type: str | None = None
    page: int | None = None
    section: str | None = None
    date: str | None = None


class SearchResponse(BaseModel):
    question: str
    results: list[SearchResult]
    total: int
    strategy: str


# =========================
# HEALTH
# =========================

class HealthResponse(BaseModel):
    status: str
    message: str


# =========================
# DOCUMENTS
# =========================

class DocumentResponse(BaseModel):
    filename: str
    reference: str | None = None
    document_type: str | None = None
    date: str | None = None
    version: str | None = None


class DocumentsResponse(BaseModel):
    total: int
    documents: list[DocumentResponse]


# =========================
# INGESTION
# =========================

class IngestRequest(BaseModel):
    strategy: Literal["fixed", "structural"] = "structural"


class IngestResponse(BaseModel):
    status: str
    message: str
    strategy: str
    indexed_chunks: int
