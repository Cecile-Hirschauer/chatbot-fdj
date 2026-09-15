class UnsafeSQLError(ValueError):
    """Raised when a SQL query contains forbidden or unsafe operations."""


def validate_sql(query: str) -> str:
    """Validate that a SQL query is safe to execute.

    Args:
        query: The SQL string to validate.

    Returns:
        The original query if it is considered safe.

    Raises:
        UnsafeSQLError: If the query contains forbidden operations.
        ValueError: If the query is empty or not a string.
    """
    raise NotImplementedError
