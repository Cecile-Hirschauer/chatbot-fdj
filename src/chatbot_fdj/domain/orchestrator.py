from chatbot_fdj.domain.llm_port import LLMPort
from chatbot_fdj.domain.prompt_builder import build_sql_prompt
from chatbot_fdj.domain.sql_validator import validate_sql


class ChatbotOrchestrator:
    """
    The main application service orchestrating the workflow between
    the user, the language model, and the domain validations.
    """

    # We reuse the exact same whitelists as defined by the FDJ database schema
    _ALLOWED_TABLES = frozenset({"draws"})
    _ALLOWED_COLUMNS = frozenset({
        "draw_year_id",
        "draw_day",
        "draw_date",
        "ball_1",
        "ball_2",
        "ball_3",
        "ball_4",
        "ball_5",
        "lucky_number"
    })

    def __init__(self, llm: LLMPort) -> None:
        # The orchestrator depends on the abstraction (LLMPort), not the concrete OpenRouter API
        self.llm = llm

    def generate_safe_sql(self, question: str) -> str:
        """
        Takes a natural language question, generates a SQL query via the LLM,
        validates it against strict security rules, and returns the safe query.
        """
        prompt = build_sql_prompt(question)
        raw_sql = self.llm.generate_sql(prompt)

        safe_sql = validate_sql(
            query=raw_sql,
            allowed_tables=self._ALLOWED_TABLES,
            allowed_columns=self._ALLOWED_COLUMNS
        )

        return safe_sql
