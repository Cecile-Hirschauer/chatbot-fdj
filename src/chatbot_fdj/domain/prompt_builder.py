_FDJ_SCHEMA = """
Table: draws
Colonnes:
- draw_year_id (TEXT): Identifiant unique combinant l'année et le numéro du tirage
- draw_day (TEXT): Jour de la semaine du tirage (ex: LUNDI, MERCREDI, SAMEDI)
- draw_date (TEXT): Date du tirage au format YYYY-MM-DD
- ball_1 (INTEGER): Premier numéro tiré
- ball_2 (INTEGER): Deuxième numéro tiré
- ball_3 (INTEGER): Troisième numéro tiré
- ball_4 (INTEGER): Quatrième numéro tiré
- ball_5 (INTEGER): Cinquième numéro tiré
- lucky_number (INTEGER): Le numéro chance
"""


def build_sql_prompt(question: str, history: list[dict[str, str]] | None = None) -> str:
    """Build the system prompt to instruct the LLM to generate a SQL query.

    Args:
        question: The user's natural language question.
        history: Optional list of previous messages in {"role": ..., "content": ...} format.
    """
    history_context = ""
    if history:
        history_context = "Recent conversation history:\n"
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            history_context += f"- {role}: {msg['content']}\n"
        history_context += (
            "\nUse this history to understand the context of the new question "
            "(pronouns, implied dates, etc.).\n\n"
        )

    return f"""Tu es un expert en base de données SQLite. Ta mission est de traduire la question de l'utilisateur en une requête SQL valide.

Schéma de la base de données :
{_FDJ_SCHEMA}

Règles strictes :
1. Retourne UNIQUEMENT la requête SQL brute. N'inclus pas de formatage markdown (comme ```sql), n'ajoute aucune explication, salutation ou autre texte.
2. Utilise UNIQUEMENT l'instruction SELECT ou WITH. N'utilise jamais DROP, UPDATE, DELETE, INSERT ou ALTER.
3. Utilise UNIQUEMENT les tables et colonnes fournies dans le schéma ci-dessus.
4. Assure-toi que la requête est parfaitement compatible avec la syntaxe SQLite.

{history_context}Question de l'utilisateur : {question}
"""
