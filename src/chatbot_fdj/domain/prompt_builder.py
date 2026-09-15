# src/chatbot_fdj/domain/prompt_builder.py

_FDJ_SCHEMA = """
Table: draws
Columns:
- draw_year_id (TEXT): Unique ID combining the year and draw number
- draw_day (TEXT): Day of the week (e.g., LUNDI, MERCREDI, SAMEDI)
- draw_date (TEXT): Date of the draw in YYYY-MM-DD format
- ball_1 (INTEGER): First drawn number
- ball_2 (INTEGER): Second drawn number
- ball_3 (INTEGER): Third drawn number
- ball_4 (INTEGER): Fourth drawn number
- ball_5 (INTEGER): Fifth drawn number
- lucky_number (INTEGER): The lucky number (numero chance)
"""

def build_sql_prompt(question: str) -> str:
    """
    Builds the system prompt to instruct the LLM to generate a SQL query.
    """
    return f"""You are a SQLite database expert. Your task is to translate the user's question into a valid SQL query.

Database Schema:
{_FDJ_SCHEMA}

Strict Rules:
1. Return ONLY the raw SQL query. Do not include markdown formatting (like ```sql), do not add explanations, greetings, or any other text.
2. Use ONLY the SELECT statement. Never use DROP, UPDATE, DELETE, INSERT, or ALTER.
3. Use ONLY the tables and columns provided in the schema above.
4. Ensure the query is perfectly compatible with SQLite syntax.

User Question: {question}
"""
