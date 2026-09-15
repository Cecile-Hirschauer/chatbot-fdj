# tests/doubles/fake_llm.py
from chatbot_fdj.domain.llm_port import LLMPort


class FakeLLM(LLMPort):
    """
    A fake implementation of LLMPort for fast, predictable unit testing
    without making real HTTP calls.
    """

    def __init__(self, expected_sql: str = "SELECT * FROM draws", expected_answer: str = "Here is the answer.") -> None:
        self.expected_sql = expected_sql
        self.expected_answer = expected_answer
        self.prompt_received = ""
        self.generate_answer_called_with = {}

    def generate_sql(self, prompt: str) -> str:
        self.prompt_received = prompt
        return self.expected_sql

    def generate_answer(self, question: str, sql_query: str, db_results: str) -> str:
        self.generate_answer_called_with = {
            "question": question,
            "sql_query": sql_query,
            "db_results": db_results
        }
        return self.expected_answer
