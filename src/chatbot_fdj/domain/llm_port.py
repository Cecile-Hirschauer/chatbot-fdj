from abc import ABC, abstractmethod


class LLMPort(ABC):
    """
    Abstract interface (Port) for Language Model interactions.
    Isolates the domain from external APIs (like OpenRouter or Mistral).
    """

    @abstractmethod
    def generate_sql(self, prompt: str) -> str:
        """
        Sends the system prompt to the LLM and returns the raw SQL query.
        """
        pass

    @abstractmethod
    def generate_answer(self, question: str, sql_query: str, db_results: str) -> str:
        """
        Generates a natural language response based on the DB results.
        """
        pass
