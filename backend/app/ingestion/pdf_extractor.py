
from pathlib import Path
import json
import fitz


# Racine du projet
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Dossiers source et destination
CORPUS_DIR = PROJECT_ROOT / "corpus"
OUTPUT_DIR = PROJECT_ROOT / "data" / "extracted"


def extract_pdf(pdf_path: Path) -> dict:
    """
    Extrait le texte d'un PDF page par page.
    """

    document = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text", sort=True)

        pages.append({
            "page": page_number,
            "text": text.strip()
        })

    result = {
        "file": pdf_path.name,
        "page_count": len(document),
        "pdf_metadata": document.metadata,
        "pages": pages
    }

    document.close()

    return result


def extract_corpus():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(CORPUS_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"Aucun PDF trouvé dans : {CORPUS_DIR}"
        )

    print(f"Nombre de PDF trouvés : {len(pdf_files)}")

    for pdf_path in pdf_files:

        print(f"\nExtraction : {pdf_path.name}")

        data = extract_pdf(pdf_path)

        # Un JSON par document
        output_path = OUTPUT_DIR / f"{pdf_path.stem}.json"

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

        print(f"Pages extraites : {data['page_count']}")
        print(f"Fichier généré : {output_path.name}")

    print("\nExtraction terminée !")


if __name__ == "__main__":
    extract_corpus()
