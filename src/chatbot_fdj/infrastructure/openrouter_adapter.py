import os

import requests
from dotenv import load_dotenv

from chatbot_fdj.domain.exceptions import LLMGenerationError
from chatbot_fdj.domain.llm_port import LLMPort

load_dotenv()

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterAdapter(LLMPort):
    """Concrete implementation of LLMPort for the OpenRouter API."""

    def __init__(self, model: str | None = None) -> None:
        # Priority: constructor arg > OPENROUTER_MODEL env var > openrouter/auto
        self.model = model or os.getenv("OPENROUTER_MODEL", "openrouter/auto")
        self.url = _OPENROUTER_URL
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def generate_sql(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=15)
        except requests.RequestException as e:
            raise LLMGenerationError(f"SQL generation request failed: {e}") from e

        if response.status_code != 200:
            raise LLMGenerationError(f"OpenRouter returned {response.status_code}: {response.text}")

        data = response.json()
        raw = data["choices"][0]["message"]["content"].strip()
        raw = raw.replace("```sql", "").replace("```", "").strip()
        if raw.endswith(";"):
            raw = raw[:-1]
        return raw

    def generate_answer(self, question: str, sql_query: str, db_results: str) -> str:
        prompt = (
            f"User question: {question}\n"
            f"SQL query executed: {sql_query}\n"
            f"Raw database result: {db_results}\n\n"
            "Write a clear, natural and concise answer in French for the user. "
            "Do not invent any data that is not present in the raw result."
        )

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=15)
        except requests.RequestException as e:
            raise LLMGenerationError(f"Answer generation request failed: {e}") from e

        if response.status_code != 200:
            raise LLMGenerationError(f"OpenRouter returned {response.status_code}: {response.text}")

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
