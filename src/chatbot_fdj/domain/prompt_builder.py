# src/chatbot_fdj/domain/prompt_builder.py

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

def build_sql_prompt(question: str) -> str:
    """
    Builds the system prompt to instruct the LLM to generate a SQL query.
    """
    return f"""Tu es un expert en base de données SQLite. Ta mission est de traduire la question de l'utilisateur en une requête SQL valide.

Schéma de la base de données :
{_FDJ_SCHEMA}

Règles strictes :
1. Retourne UNIQUEMENT la requête SQL brute. N'inclus pas de formatage markdown (comme ```sql), n'ajoute aucune explication, salutation ou autre texte.
2. Utilise UNIQUEMENT l'instruction SELECT. N'utilise jamais DROP, UPDATE, DELETE, INSERT ou ALTER.
3. Utilise UNIQUEMENT les tables et colonnes fournies dans le schéma ci-dessus.
4. Assure-toi que la requête est parfaitement compatible avec la syntaxe SQLite.

Question de l'utilisateur : {question}
"""
