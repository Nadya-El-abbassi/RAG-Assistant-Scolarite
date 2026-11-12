
import pytest

from app.ingestion.chunker import (
    fixed_size_chunking,
    structural_chunking,
    build_document_chunks,
    generate_chunk_id
)


# ==========================================
# 1. FIXED-SIZE CHUNKING
# ==========================================

def test_fixed_chunking_returns_chunks():
    text = "A" * 1200

    chunks = fixed_size_chunking(
        text,
        chunk_size=500,
        overlap=100
    )

    assert len(chunks) == 3
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_fixed_chunking_overlap():
    text = "A" * 1000

    chunks = fixed_size_chunking(
        text,
        chunk_size=500,
        overlap=100
    )

    assert chunks[0][-100:] == chunks[1][:100]


def test_fixed_chunking_empty_text():
    assert fixed_size_chunking("   ") == []


def test_fixed_chunking_invalid_parameters():
    with pytest.raises(ValueError):
        fixed_size_chunking("Test", chunk_size=0)

    with pytest.raises(ValueError):
        fixed_size_chunking("Test", chunk_size=500, overlap=500)


# ==========================================
# 2. STRUCTURAL CHUNKING
# ==========================================

def test_structural_chunking_detects_articles():
    text = """
    Article 1 : Inscription
    Les étudiants doivent procéder à leur inscription.

    Article 2 : Évaluation
    Les étudiants sont évalués durant chaque semestre.
    """

    chunks = structural_chunking(text)

    assert len(chunks) == 2
    assert chunks[0]["section"] == "Article 1 : Inscription"
    assert chunks[1]["section"] == "Article 2 : Évaluation"


def test_structural_chunking_empty_text():
    assert structural_chunking("   ") == []


def test_structural_chunking_invalid_size():
    with pytest.raises(ValueError):
        structural_chunking("Texte de test", max_size=0)


# ==========================================
# 3. CHUNK METADATA
# ==========================================

def test_build_document_chunks_metadata():
    document = {
        "file": "reglement.pdf",
        "metadata": {
            "reference": "REF-001",
            "type": "reglement",
            "date": "2026-07-10",
            "version": "2026-2027",
            "status": "official"
        },
        "pages": [
            {
                "page": 1,
                "text": "Article 1 : Inscription\nLes étudiants doivent s'inscrire."
            }
        ]
    }

    chunks = build_document_chunks(
        document=document,
        strategy="structural",
        chunk_size=500,
        overlap=100
    )

    assert len(chunks) > 0

    chunk = chunks[0]

    assert chunk["file"] == "reglement.pdf"
    assert chunk["reference"] == "REF-001"
    assert chunk["type"] == "reglement"
    assert chunk["page"] == 1
    assert chunk["section"] == "Article 1 : Inscription"
    assert chunk["strategy"] == "structural"


# ==========================================
# 4. STABLE CHUNK ID
# ==========================================

def test_chunk_id_is_stable():
    id1 = generate_chunk_id(
        "reglement.pdf", 1, 0, "Texte de test"
    )

    id2 = generate_chunk_id(
        "reglement.pdf", 1, 0, "Texte de test"
    )

    assert id1 == id2
