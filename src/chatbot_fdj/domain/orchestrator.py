import re
import sqlite3
from pathlib import Path

from chatbot_fdj.domain.llm_port import LLMPort
from chatbot_fdj.domain.prompt_builder import build_sql_prompt
from chatbot_fdj.domain.sql_validator import validate_sql

_DEFAULT_DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "lottery.db"

_REFUSAL_MESSAGE = (
    "Je ne suis pas autorisé à modifier ou simuler des tirages. "
    "Je ne peux que consulter l'historique officiel."
)

# Keywords that indicate an attempt to modify, simulate or invent draw data.
# Checked in Python before the LLM is called, so no LLM compliance is required.
_MODIFICATION_PATTERNS: list[str] = [
    # Replace / modify (imperative and infinitive forms)
    r"\bremplace\b",
    r"\bremplacer\b",
    r"\bmodifie\b",
    r"\bmodifier\b",
    # "change" as imperative/infinitive (blocks "change le", "changer"),
    # but NOT "changé" (past participle) or "changement" (noun) which appear in valid queries
    r"\bchanger\b",
    r"\bchange\s+le\b",
    r"\bchange\s+la\b",
    r"\bchange\s+les\b",
    r"\bchange\s+un\b",
    r"\baltère\b",
    r"\baltérer\b",
    # Delete / add
    r"\bsupprime\b",
    r"\bsupprimer\b",
    r"\bajoute\b",
    r"\bajouter\b",
    # Simulate / invent / imagine / suppose
    r"\bsimule\b",
    r"\bsimuler\b",
    r"\binvente\b",
    r"\binventer\b",
    r"\bimagin\w+\b",
    r"\bsuppose\b",
    r"\bsupposer\b",
    # Create / generate (fictional draw)
    r"\bcré[ée]\b",
    r"\bcréer\b",
    r"\bgénère\b",
    r"\bgénérer\b",
    # Hypothetical phrases
    r"\bet si\b",
    r"\bque se passerait\b",
    r"\bque se passer\b",
]

_MODIFICATION_RE = re.compile(
    "|".join(_MODIFICATION_PATTERNS),
    re.IGNORECASE,
)


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
        """Initialise the orchestrator.

        Args:
            llm: Concrete implementation of :class:`LLMPort` used for SQL
                generation and answer synthesis.
            db_path: Path to the SQLite database file. Defaults to
                ``data/lottery.db`` relative to the project root.
        """
        self.llm = llm
        self.db_path = db_path or _DEFAULT_DB_PATH

    def generate_safe_sql(
        self, question: str, history: list[dict[str, str]] | None = None
    ) -> str:
        """Generate and validate a SQL query from a natural language question."""
        prompt = build_sql_prompt(question, history)
        raw_sql = self.llm.generate_sql(prompt)

        return validate_sql(
            query=raw_sql,
            allowed_tables=self._ALLOWED_TABLES,
        )

    def _execute_sql(self, sql: str) -> str:
        """Execute a validated SQL query and return results as a formatted string.

        The database is opened in read-only mode (``?mode=ro``) via the SQLite
        URI syntax. Any write attempt will raise ``sqlite3.OperationalError``
        immediately, providing a second line of defence after the SQL validator.
        """
        db_uri = f"file:{self.db_path.absolute()}?mode=ro"
        with sqlite3.connect(db_uri, uri=True) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql)
            rows = cursor.fetchmany(50)
            if not rows:
                return "No results found."
            headers = rows[0].keys()
            lines = [" | ".join(headers)]
            lines += [" | ".join(str(row[col]) for col in headers) for row in rows]
            return "\n".join(lines)

    @staticmethod
    def _is_modification_attempt(question: str) -> bool:
        """Return True if the question contains modification or simulation keywords.

        This check runs in Python before the LLM is involved, making it
        immune to prompt injection and LLM non-compliance.
        """
        return bool(_MODIFICATION_RE.search(question))

    def answer_question(
        self, question: str, history: list[dict[str, str]] | None = None
    ) -> tuple[str, str, str]:
        """Run the full pipeline: SQL generation → DB execution → natural language answer.

        If the question is detected as a modification or simulation attempt,
        the pipeline is short-circuited and a fixed refusal message is returned
        without calling the LLM for the answer step.

        Returns:
            A tuple of (safe_sql, db_results, answer).
        """
        if self._is_modification_attempt(question):
            return "", "", _REFUSAL_MESSAGE

        safe_sql = self.generate_safe_sql(question, history)
        db_results = self._execute_sql(safe_sql)
        answer = self.llm.generate_answer(question, safe_sql, db_results)
        return safe_sql, db_results, answer
