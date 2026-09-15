from abc import ABC, abstractmethod


class LLMPort(ABC):
    """
    Abstract interface (Port) for Language Model interactions.
    Isolates the domain from external APIs (like OpenRouter or Mistral).
    """

    @abstractmethod
    def generate_sql(self, prompt: str) -> str:
        """Send a prompt to the LLM and return a raw SQL query string.

        Args:
            prompt: The full instruction prompt describing the schema, rules,
                and the user's question.

        Returns:
            A raw SQL string as returned by the model (may contain markdown
            fences or a trailing semicolon — callers are responsible for
            cleaning up if needed).

        Raises:
            LLMGenerationError: If the request to the model fails.
        """

    @abstractmethod
    def generate_answer(self, question: str, sql_query: str, db_results: str) -> str:
        """Generate a natural language answer from query results.

        Args:
            question: The original user question in natural language.
            sql_query: The validated SQL query that was executed.
            db_results: The formatted string of rows returned by the database.

        Returns:
            A human-readable answer in French based solely on the provided data.

        Raises:
            LLMGenerationError: If the request to the model fails.
        """
