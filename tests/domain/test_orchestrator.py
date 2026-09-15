import pytest

from chatbot_fdj.domain.exceptions import UnsafeSQLError
from chatbot_fdj.domain.orchestrator import ChatbotOrchestrator
from tests.doubles.fake_llm import FakeLLM


class TestChatbotOrchestrator:
    def test_generate_safe_sql_returns_valid_query(self):
        # Arrange : Je configure mon faux LLM pour renvoyer une requête inoffensive
        fake_llm = FakeLLM(expected_sql="SELECT draw_date FROM draws")
        orchestrator = ChatbotOrchestrator(llm=fake_llm)
        question = "Quand a eu lieu le dernier tirage ?"

        # Act
        result_sql = orchestrator.generate_safe_sql(question)

        # Assert : Je vérifie que la requête est renvoyée et que le LLM a bien reçu la question
        assert result_sql == "SELECT draw_date FROM draws"
        assert question in fake_llm.prompt_received

    def test_generate_safe_sql_blocks_malicious_query(self):
        # Arrange : Le LLM devient fou et renvoie une requête destructrice
        fake_llm = FakeLLM(expected_sql="DROP TABLE draws")
        orchestrator = ChatbotOrchestrator(llm=fake_llm)

        # Act & Assert : L'orchestrateur doit bloquer la requête en levant l'exception
        with pytest.raises(UnsafeSQLError):
            orchestrator.generate_safe_sql("Supprime les données")
