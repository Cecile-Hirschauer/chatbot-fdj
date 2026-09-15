import os

import requests
from dotenv import load_dotenv

from chatbot_fdj.domain.exceptions import LLMGenerationError
from chatbot_fdj.domain.llm_port import LLMPort

# Charge les variables du fichier .env
load_dotenv()


class OpenRouterAdapter(LLMPort):
    """
    Implémentation concrète de LLMPort pour l'API OpenRouter.
    """

    def __init__(self, model: str = "mistralai/mistral-7b-instruct:free") -> None:
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("La variable OPENROUTER_API_KEY est introuvable dans le .env")

        self.model = model
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",  # Recommandé par OpenRouter
            "X-Title": "Chatbot FDJ",
        }

    def generate_sql(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,  # Strictement 0 pour du code déterministe
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise LLMGenerationError(f"Échec de la génération SQL via OpenRouter : {str(e)}")  # noqa: B904

    def generate_answer(self, question: str, sql_query: str, db_results: str) -> str:
        prompt = (
            f"Voici la question de l'utilisateur : {question}\n"
            f"Voici la requête SQL exécutée : {sql_query}\n"
            f"Voici le résultat brut de la base de données : {db_results}\n\n"
            "Rédige une réponse claire, naturelle et concise en français pour l'utilisateur. "
            "N'invente aucune donnée qui ne soit pas dans le résultat brut."
        )

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,  # Légèrement plus élevé pour un langage plus naturel
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise LLMGenerationError(f"Échec de la génération de la réponse via OpenRouter : {str(e)}")  # noqa: B904
