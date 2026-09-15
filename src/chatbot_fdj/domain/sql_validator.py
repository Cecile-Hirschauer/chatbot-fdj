import re

_FORBIDDEN_KEYWORDS: frozenset[str] = frozenset(
    {"DROP", "DELETE", "INSERT", "UPDATE", "TRUNCATE", "CREATE", "ALTER"}
)


class UnsafeSQLError(ValueError):
    """Raised when a SQL query contains forbidden or unsafe operations."""


def validate_sql(query: str) -> str:
    """Validate that a SQL query is safe to execute.

    Only read-only SELECT statements are allowed. Any mutation keyword,
    multiple statements, or non-string input is rejected immediately.

    Args:
        query: The SQL string to validate.

    Returns:
        The original query if it is considered safe.

    Raises:
        TypeError: If query is not a string.
        ValueError: If the query is empty or blank.
        UnsafeSQLError: If the query contains forbidden operations.
    """
    if not isinstance(query, str):
        raise TypeError(f"query must be a string, got {type(query).__name__}")

    stripped = query.strip()
    if not stripped:
        raise ValueError("query must not be empty")

    if ";" in stripped:
        raise UnsafeSQLError("Multiple statements are not allowed")

    upper = stripped.upper()

    for keyword in _FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper):
            raise UnsafeSQLError(f"Forbidden keyword '{keyword}' is not allowed")

    if not upper.startswith("SELECT"):
        raise UnsafeSQLError("Only SELECT queries are allowed")

    return query
