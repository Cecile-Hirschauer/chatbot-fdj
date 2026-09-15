# tests/domain/test_prompt_builder.py

from chatbot_fdj.domain.prompt_builder import build_sql_prompt


class TestPromptBuilder:
    def test_prompt_contains_user_question(self):
        question = "Quel est le numéro chance le plus fréquent ?"
        prompt = build_sql_prompt(question)
        assert question in prompt

    def test_prompt_contains_database_schema(self):
        prompt = build_sql_prompt("question bidon")

        # Check if the table and some key columns are mentioned (these remain in English)
        assert "draws" in prompt
        assert "draw_date" in prompt
        assert "lucky_number" in prompt
        assert "ball_1" in prompt

    def test_prompt_contains_strict_rules(self):
        prompt = build_sql_prompt("question bidon")

        # Check if the security rules are present in French
        assert "UNIQUEMENT" in prompt
        assert "SELECT" in prompt
        assert "Schéma" in prompt
