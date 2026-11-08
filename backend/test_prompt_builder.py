from app.generation.prompt_builder import build_prompt

results = [
    {
        "content": (
            "La durée minimale du PFE est portée "
            "de 16 semaines à 18 semaines."
        ),
        "source": "07_Note_de_service_2026-14.pdf",
        "reference": "EIH-DE-NS-2026-14",
        "document_type": "Note de service",
        "date": "5 octobre 2026",
        "page": 1
    },
    {
        "content": (
            "La durée du PFE est comprise entre "
            "16 et 24 semaines."
        ),
        "source": "02_Guide_stages_PFE_2026.pdf",
        "reference": "EIH-SRE-GUIDE-2026",
        "document_type": "Guide pratique",
        "date": "15 juin 2026",
        "page": 2
    }
]

prompt = build_prompt(
    "Quelle est la durée minimale du stage PFE ?",
    results
)

print("===== SYSTEM PROMPT =====")
print(prompt["system"])

print("\n===== USER PROMPT =====")
print(prompt["user"])