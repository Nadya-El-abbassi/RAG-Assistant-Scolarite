
from pathlib import Path
from typing import Optional
import json
import re
import hashlib


# =====================================================
# CONFIGURATION
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_DIR = PROJECT_ROOT / "data" / "cleaned"
OUTPUT_DIR = PROJECT_ROOT / "data" / "chunks"

DEFAULT_CHUNK_SIZE = 500
DEFAULT_OVERLAP = 100
DEFAULT_STRUCTURAL_MAX_SIZE = 1200


# =====================================================
# IDENTIFIANT UNIQUE ET STABLE
# =====================================================

def generate_chunk_id(
    filename: str,
    page: int,
    index: int,
    content: str
) -> str:

    raw = f"{filename}_{page}_{index}_{content}"

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:16]


# =====================================================
# STRATEGIE 1 : FIXED-SIZE CHUNKING
# =====================================================

def fixed_size_chunking(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP
) -> list[str]:

    if chunk_size <= 0:
        raise ValueError("chunk_size doit être positif")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap doit être positif et inférieur à chunk_size"
        )

    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


# =====================================================
# DETECTION DES SECTIONS
# =====================================================

def is_heading(line: str) -> bool:

    line = line.strip()

    patterns = [
        r"^(CHAPITRE|TITRE|PARTIE)\s+",
        r"^Article\s+\d+",
        r"^Question\s*:",
        r"^\d+(?:\.\d+)*\s+"
    ]

    return any(
        re.match(pattern, line, re.IGNORECASE)
        for pattern in patterns
    )


def extract_section(lines: list[str]) -> Optional[str]:

    for line in lines:

        line = line.strip()

        if is_heading(line):
            return line

    return None


# =====================================================
# STRATEGIE 2 : STRUCTURAL CHUNKING
# =====================================================

def structural_chunking(
    text: str,
    max_size: int = DEFAULT_STRUCTURAL_MAX_SIZE
) -> list[dict]:

    if max_size <= 0:
        raise ValueError("max_size doit être positif")

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return []

    sections = []
    current_section = []
    current_title = "Introduction"

    for line in lines:

        if is_heading(line) and current_section:

            sections.append({
                "section": current_title,
                "text": "\n".join(current_section)
            })

            current_section = []
            current_title = line

        elif is_heading(line):
            current_title = line

        current_section.append(line)

    if current_section:

        sections.append({
            "section": current_title,
            "text": "\n".join(current_section)
        })

    # Découper les sections trop longues
    final_chunks = []

    for section in sections:

        content = section["text"]

        if len(content) <= max_size:

            final_chunks.append(section)

        else:

            sub_chunks = fixed_size_chunking(
                content,
                chunk_size=max_size,
                overlap=min(100, max_size - 1)
            )

            for sub_chunk in sub_chunks:

                final_chunks.append({
                    "section": section["section"],
                    "text": sub_chunk
                })

    return final_chunks


# =====================================================
# CONSTRUCTION DES CHUNKS AVEC METADONNEES
# =====================================================

def build_document_chunks(
    document: dict,
    strategy: str,
    chunk_size: int,
    overlap: int
) -> list[dict]:

    all_chunks = []

    filename = document["file"]
    metadata = document["metadata"]

    reference = metadata.get("reference")
    doc_type = metadata.get("type")
    doc_date = metadata.get("date")
    version = metadata.get("version")
    status = metadata.get("status")

    chunk_index = 0

    for page_data in document["pages"]:

        page_number = page_data["page"]
        page_text = page_data["text"]

        if strategy == "fixed":

            pieces = fixed_size_chunking(
                page_text,
                chunk_size,
                overlap
            )

            pieces = [
                {
                    "section": extract_section(piece.splitlines()),
                    "text": piece
                }
                for piece in pieces
            ]

        elif strategy == "structural":

            pieces = structural_chunking(
                page_text,
                max_size=chunk_size
            )

        else:
            raise ValueError(
                "Stratégie inconnue : utiliser fixed ou structural"
            )

        for piece in pieces:

            content = piece["text"].strip()

            if not content:
                continue

            chunk_id = generate_chunk_id(
                filename,
                page_number,
                chunk_index,
                content
            )

            all_chunks.append({

                "id": chunk_id,

                "chunk_id": chunk_id,

                "text": content,

                "file": filename,

                "reference": reference,

                "type": doc_type,

                "date": doc_date,

                "version": version,

                "status": status,

                "page": page_number,

                "section": piece["section"],

                "strategy": strategy

            })

            chunk_index += 1

    return all_chunks


# =====================================================
# INGESTION DES DOCUMENTS
# =====================================================

def chunk_corpus(
    strategy: str = "fixed",
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP
):

    if strategy not in ("fixed", "structural"):
        raise ValueError(
            "strategy doit être fixed ou structural"
        )

    if chunk_size <= 0:
        raise ValueError("chunk_size doit être positif")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap invalide")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    json_files = sorted(INPUT_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            "Aucun document nettoyé trouvé"
        )

    all_chunks = []

    for file_path in json_files:

        print(f"\nTraitement : {file_path.name}")

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            document = json.load(file)

        chunks = build_document_chunks(
            document=document,
            strategy=strategy,
            chunk_size=chunk_size,
            overlap=overlap
        )

        all_chunks.extend(chunks)

        print(f"Chunks générés : {len(chunks)}")

    # Export JSON
    output_path = OUTPUT_DIR / f"chunks_{strategy}.json"

    result = {
        "strategy": strategy,
        "chunk_size": chunk_size,
        "overlap": overlap,
        "total_chunks": len(all_chunks),
        "chunks": all_chunks
    }

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n================================")
    print("CHUNKING TERMINE")
    print("Stratégie :", strategy)
    print("Total chunks :", len(all_chunks))
    print("Fichier :", output_path)
    print("================================")


if __name__ == "__main__":

    chunk_corpus(
        strategy="fixed",
        chunk_size=500,
        overlap=100
    )
