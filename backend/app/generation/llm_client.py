import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class LLMClient:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile"
        )

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY est absente du fichier .env"
            )

        self.client = Groq(api_key=api_key)

    def generate(self, system_prompt: str, user_prompt: str):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )

        return response.choices[0].message.content


if __name__ == "__main__":

    llm = LLMClient()

    answer = llm.generate(
        system_prompt="Tu es un assistant qui répond en français.",
        user_prompt="Explique brièvement ce qu'est un RAG."
    )

    print("\nRéponse du LLM :")
    print(answer)