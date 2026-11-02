
from pathlib import Path
from collections import Counter
import json
import re
import math


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_DIR = PROJECT_ROOT / "data" / "extracted"
OUTPUT_DIR = PROJECT_ROOT / "data" / "cleaned"


def normalize_line(line: str) -> str:
    """Normalise une ligne pour comparer les en-têtes."""

    return re.sub(r"\s+", " ", line).strip()


def extract_metadata(pages: list) -> dict:
    """
    Extrait les métadonnées officielles depuis le texte brut.
    """

    full_text = "\n".join(page["text"] for page in pages)

    metadata = {
        "reference": None,
        "type": None,
        "date": None,
        "version": None,
        "status": None
    }

    patterns = {
        "reference": r"Référence\s+([A-Z0-9][A-Z0-9-]+)",
        "type": r"Type de document\s+(.+)",
        "date": r"Date de publication\s+(.+)",
        "version": r"Version\s+([0-9]+(?:\.[0-9]+)*)",
        "status": r"Statut\s+(.+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, full_text, re.IGNORECASE)

        if match:
            metadata[key] = normalize_line(match.group(1))

    status_match = re.search(
    r"Statut\s+(.+?)(?=\n\s*\n)",
    full_text,
    re.IGNORECASE | re.DOTALL
    )
    if status_match:
        metadata["status"] = normalize_line(status_match.group(1))

    return metadata


def find_repeated_headers_footers(pages: list) -> set:
    """
    Identifie les lignes répétées en haut ou en bas
    des pages.
    """

    candidates = []

    for page in pages:
        lines = [
            normalize_line(line)
            for line in page["text"].splitlines()
            if normalize_line(line)
        ]

        # Les trois premières et dernières lignes
        candidates.extend(lines[:3])
        candidates.extend(lines[-3:])

    counts = Counter(candidates)

    page_count = len(pages)
    threshold = max(2, math.ceil(page_count * 0.6))

    return {
        line
        for line, count in counts.items()
        if count >= threshold
    }


def clean_page(text: str, repeated_lines: set) -> str:
    """
    Nettoie une page sans supprimer les retours
    à la ligne utiles aux tableaux.
    """

    cleaned_lines = []

    for line in text.splitlines():

        normalized = normalize_line(line)

        if not normalized:
            continue

        if normalized in repeated_lines:
            continue

        cleaned_lines.append(normalized)

    return "\n".join(cleaned_lines)


def clean_document(data: dict) -> dict:
    """
    Nettoie un document et enrichit ses métadonnées.
    """

    pages = data["pages"]

    # Extraction des métadonnées avant le nettoyage
    metadata = extract_metadata(pages)

    # Détection des en-têtes et pieds de page
    repeated_lines = find_repeated_headers_footers(pages)

    cleaned_pages = []

    for page in pages:

        cleaned_text = clean_page(
            page["text"],
            repeated_lines
        )

        cleaned_pages.append({
            "page": page["page"],
            "text": cleaned_text
        })

    return {
        "file": data["file"],
        "page_count": data["page_count"],
        "metadata": metadata,
        "pages": cleaned_pages
    }


def clean_corpus():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    json_files = sorted(INPUT_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            "Aucun fichier JSON trouvé dans data/extracted"
        )

    for file_path in json_files:

        print(f"\nNettoyage : {file_path.name}")

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        cleaned_data = clean_document(data)

        output_path = OUTPUT_DIR / file_path.name

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(
                cleaned_data,
                file,
                ensure_ascii=False,
                indent=4
            )

        print("Référence :", cleaned_data["metadata"]["reference"])
        print("Type :", cleaned_data["metadata"]["type"])
        print("Date :", cleaned_data["metadata"]["date"])
        print("Version :", cleaned_data["metadata"]["version"])
        print("Statut :", cleaned_data["metadata"]["status"])

    print("\nNettoyage du corpus terminé !")


if __name__ == "__main__":
    clean_corpus()
