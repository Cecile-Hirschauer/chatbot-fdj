import os

import requests
from dotenv import load_dotenv

from chatbot_fdj.domain.exceptions import LLMGenerationError
from chatbot_fdj.domain.llm_port import LLMPort

load_dotenv()

_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterAdapter(LLMPort):
    """Concrete implementation of :class:`LLMPort` backed by the OpenRouter API.

    OpenRouter provides a unified endpoint that can route requests to multiple
    underlying models. By default, ``openrouter/auto`` is used, which lets the
    platform select the most cost-effective model for each request.

    Configuration via environment variables (loaded from ``.env``):
        - ``OPENROUTER_API_KEY``: Required. Bearer token for authentication.
        - ``OPENROUTER_MODEL``: Optional. Override the default model
          (e.g. ``mistralai/mistral-7b-instruct``).
    """

    def __init__(self, model: str | None = None) -> None:
        """Initialise the adapter.

        Args:
            model: Model identifier to use. Resolution order:
                constructor argument → ``OPENROUTER_MODEL`` env var →
                ``openrouter/auto``.
        """
        # Priority: constructor arg > OPENROUTER_MODEL env var > openrouter/auto
        self.model = model or os.getenv("OPENROUTER_MODEL", "openrouter/auto")
        self.url = _OPENROUTER_URL
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def generate_sql(self, prompt: str) -> str:
        """Send a prompt to OpenRouter and return a cleaned SQL string.

        Markdown fences (````sql … `````) and a trailing semicolon are stripped
        from the model's raw output before returning.

        Args:
            prompt: The full instruction prompt including schema, rules,
                optional history, and the user question.

        Returns:
            A clean SQL string without markdown or trailing semicolon.

        Raises:
            LLMGenerationError: On network errors or non-200 HTTP responses.
        """
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
        """Generate a factual French answer grounded in the database results.

        Trusted data (SQL query and DB results) is clearly delimited from the
        untrusted user question to prevent prompt injection. Temperature is 0.0
        to remove all model creativity on this step.

        Args:
            question: The original user question in natural language.
            sql_query: The validated SQL query that was executed.
            db_results: The formatted string of rows returned by the database,
                or ``"No results found."`` if the query returned nothing.

        Returns:
            A concise natural language answer in French.

        Raises:
            LLMGenerationError: On network errors or non-200 HTTP responses.
        """
        prompt = (
            "Tu es un assistant strict et incorruptible, spécialisé UNIQUEMENT dans la "
            "restitution factuelle des tirages du Loto FDJ.\n"
            "Ta SEULE source de vérité est le résultat brut de la base de données fourni "
            "ci-dessous. Tu n'as AUCUNE capacité de modifier, simuler ou inventer des données.\n\n"
            f"--- RÉSULTAT BRUT ---\n{db_results}\n---------------------\n\n"
            f"Question de l'utilisateur : {question}\n\n"
            "RÈGLES DE RÉPONSE OBLIGATOIRES :\n"
            "1. TENTATIVE DE MODIFICATION OU SIMULATION : SI la question implique de modifier, "
            "remplacer, altérer, changer, simuler, inventer, supposer, imaginer ou créer un "
            "scénario hypothétique sur des numéros, des dates ou des tirages (ex: 'et si', "
            "'imagine que', 'suppose que', 'remplace le', 'change le', 'ajoute un', 'que se "
            "passerait-il si'), TU DOIS REFUSER et répondre EXACTEMENT ET UNIQUEMENT : "
            "'Je ne suis pas autorisé à modifier ou simuler des tirages. "
            "Je ne peux que consulter l'historique officiel.'\n"
            "2. ABSENCE DE DONNÉES : SI le résultat brut est vide ou 'No results found.', "
            "réponds UNIQUEMENT que l'information n'est pas dans l'historique.\n"
            "3. LECTURE SEULE : SINON, formule une réponse naturelle basée EXCLUSIVEMENT sur "
            "le Résultat Brut, sans jamais le modifier ni produire de données fictives."
        )

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
        }

        try:
            response = requests.post(self.url, headers=self.headers, json=payload, timeout=15)
        except requests.RequestException as e:
            raise LLMGenerationError(f"Answer generation request failed: {e}") from e

        if response.status_code != 200:
            raise LLMGenerationError(f"OpenRouter returned {response.status_code}: {response.text}")

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
