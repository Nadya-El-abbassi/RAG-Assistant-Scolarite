REFUSAL_MESSAGE = (
    "Je ne trouve pas cette information dans les documents de l'École."
)


def build_prompt(question: str, results: list[dict]) -> dict:
    """
    Construit le prompt envoyé au LLM à partir
    de la question et des chunks retrouvés.
    """

    if not results:
        return {
            "system": "",
            "user": REFUSAL_MESSAGE
        }

    context_parts = []

    for index, result in enumerate(results, start=1):

        metadata = result.get("metadata", {})

        # Notre SearchEngine utilise aussi directement ces champs.
        source = result.get("source") or metadata.get("file", "Source inconnue")
        reference = result.get("reference") or metadata.get("reference", "N/A")
        page = result.get("page") or metadata.get("page", "N/A")
        date = result.get("date") or metadata.get("date", "N/A")
        doc_type = (
            result.get("document_type")
            or metadata.get("type", "N/A")
        )

        content = result.get("content") or result.get("text", "")

        context_parts.append(
            f"""
[SOURCE {index}]
Document : {source}
Référence : {reference}
Type : {doc_type}
Date : {date}
Page : {page}

Contenu :
{content}
"""
        )

    context = "\n".join(context_parts)

    system_prompt = f"""
Tu es Assistant Scolarité de l'École d'Ingénieurs Hélianthe (EIH).

Ton rôle est de répondre aux questions des étudiants
en utilisant exclusivement les documents fournis.

RÈGLES OBLIGATOIRES :

1. Utilise uniquement les informations présentes dans le contexte.
2. N'invente aucune information.
3. Si les documents ne contiennent pas la réponse,
   réponds exactement :
   "{REFUSAL_MESSAGE}"
4. Ajoute les citations sous la forme [1], [2], etc.
5. Chaque citation doit correspondre à une source fournie.
6. Si plusieurs documents présentent des règles contradictoires :
   - Vérifie si un document déclare explicitement modifier
     ou remplacer une disposition antérieure.
   - Vérifie son champ d'application.
   - Si la modification s'applique à la question,
     privilégie la nouvelle disposition.
   - Signale brièvement le changement à l'étudiant.
   - Ne considère pas automatiquement qu'un document
     est prioritaire uniquement parce qu'il est plus récent.
7. Réponds clairement et en français.

CONTEXTE DOCUMENTAIRE :

{context}
"""

    user_prompt = f"""
Question de l'étudiant :
{question}

Réponds à cette question en respectant toutes les règles.
"""

    return {
        "system": system_prompt,
        "user": user_prompt
    }