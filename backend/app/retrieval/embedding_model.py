
from sentence_transformers import SentenceTransformer


class EmbeddingModel:

    def __init__(self):

        self.model_name = (
            "sentence-transformers/"
            "paraphrase-multilingual-MiniLM-L12-v2"
        )

        print("Chargement du modèle d'embeddings...")

        self.model = SentenceTransformer(
            self.model_name,
            device="cpu"
        )

        print("Modèle chargé avec succès !")

    def encode(self, texts: list[str]):

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return embeddings

    def encode_query(self, question: str):

        embedding = self.model.encode(
            [question],
            normalize_embeddings=True
        )

        return embedding[0].tolist()


if __name__ == "__main__":

    embedding_model = EmbeddingModel()

    texts = [
        "La durée minimale du PFE est de 18 semaines.",
        "Le projet de fin d'études dure au minimum 18 semaines.",
        "Le restaurant de l'École propose des repas aux étudiants."
    ]

    vectors = embedding_model.encode(texts)

    print("Nombre de textes :", len(vectors))
    print("Dimensions :", vectors.shape)
