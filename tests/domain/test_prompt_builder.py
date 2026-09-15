from chatbot_fdj.domain.prompt_builder import build_sql_prompt


class TestPromptBuilder:
    def test_prompt_contains_user_question(self):
        question = "What is the most frequent lucky number?"
        prompt = build_sql_prompt(question)
        assert question in prompt

    def test_prompt_contains_database_schema(self):
        prompt = build_sql_prompt("dummy question")

        # Check if the table and some key columns are mentioned
        assert "draws" in prompt
        assert "draw_date" in prompt
        assert "lucky_number" in prompt
        assert "ball_1" in prompt

    def test_prompt_contains_strict_rules(self):
        prompt = build_sql_prompt("dummy question")

        # Check if the security and output format rules are present
        assert "SELECT" in prompt.upper()
        assert "ONLY" in prompt.upper() or "WITHOUT" in prompt.upper()
