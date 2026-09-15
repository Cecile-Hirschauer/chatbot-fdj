import sqlite3
from pathlib import Path

from chatbot_fdj.domain.llm_port import LLMPort
from chatbot_fdj.domain.prompt_builder import build_sql_prompt
from chatbot_fdj.domain.sql_validator import validate_sql

_DEFAULT_DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "lottery.db"


class ChatbotOrchestrator:
    """
    The main application service orchestrating the workflow between
    the user, the language model, and the domain validations.
    """

    _ALLOWED_TABLES = frozenset({"draws"})
    _ALLOWED_COLUMNS = frozenset(
        {
            "draw_year_id",
            "draw_day",
            "draw_date",
            "ball_1",
            "ball_2",
            "ball_3",
            "ball_4",
            "ball_5",
            "lucky_number",
        }
    )

    def __init__(self, llm: LLMPort, db_path: Path | None = None) -> None:
        self.llm = llm
        self.db_path = db_path or _DEFAULT_DB_PATH

    def generate_safe_sql(self, question: str) -> str:
        """Generate and validate a SQL query from a natural language question."""
        prompt = build_sql_prompt(question)
        raw_sql = self.llm.generate_sql(prompt)
        print(f"[DEBUG] Raw SQL from LLM: {raw_sql}")  # TODO: remove before production

        return validate_sql(
            query=raw_sql,
            allowed_tables=self._ALLOWED_TABLES,
        )

    def _execute_sql(self, sql: str) -> str:
        """Execute a validated SQL query and return results as a formatted string."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql)
            rows = cursor.fetchmany(50)
            if not rows:
                return "No results found."
            headers = rows[0].keys()
            lines = [" | ".join(headers)]
            lines += [" | ".join(str(row[col]) for col in headers) for row in rows]
            return "\n".join(lines)

    def answer_question(self, question: str) -> tuple[str, str, str]:
        """Run the full pipeline: SQL generation → DB execution → natural language answer.

        Returns:
            A tuple of (safe_sql, db_results, answer).
        """
        safe_sql = self.generate_safe_sql(question)
        db_results = self._execute_sql(safe_sql)
        answer = self.llm.generate_answer(question, safe_sql, db_results)
        return safe_sql, db_results, answer
