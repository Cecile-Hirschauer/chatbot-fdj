import re

from chatbot_fdj.domain.exceptions import UnsafeSQLError

_FORBIDDEN_KEYWORDS: frozenset[str] = frozenset(
    {"DROP", "DELETE", "INSERT", "UPDATE", "TRUNCATE", "CREATE", "ALTER"}
)


def _extract_referenced_tables(upper: str) -> set[str]:
    """Extract table names referenced after FROM and JOIN keywords."""
    tables: set[str] = set()
    tables.update(re.findall(r"\bFROM\s+(\w+)", upper))
    tables.update(re.findall(r"\bJOIN\s+(\w+)", upper))
    return tables


def _extract_referenced_columns(upper: str) -> set[str]:
    """Extract column names from the SELECT clause.

    Returns an empty set if the clause uses a wildcard (*), meaning no
    per-column check is needed.
    """
    match = re.match(r"SELECT\s+(.*?)\s+FROM\b", upper, re.DOTALL)
    if not match:
        return set()

    cols_str = match.group(1).strip()
    if cols_str == "*":
        return set()

    columns: set[str] = set()
    for raw in cols_str.split(","):
        col = raw.strip()
        # table.column → keep only the column part
        if "." in col:
            col = col.split(".")[-1].strip()
        # aggregate like COUNT(col) or COUNT(*) → extract inner token
        func_match = re.match(r"\w+\((\w+|\*)\)", col)
        if func_match:
            inner = func_match.group(1)
            if inner != "*":
                columns.add(inner)
            continue
        if col and col != "*":
            columns.add(col)
    return columns


def validate_sql(
    query: str,
    allowed_tables: frozenset[str] | None = None,
    allowed_columns: frozenset[str] | None = None,
) -> str:
    """Validate that a SQL query is safe to execute.

    Only read-only SELECT statements are allowed. When whitelists are
    provided, every referenced table and column must appear in them.

    Args:
        query: The SQL string to validate.
        allowed_tables: If provided, only these table names are permitted.
        allowed_columns: If provided, only these column names are permitted.
            A bare ``SELECT *`` always passes regardless of this whitelist.

    Returns:
        The original query if it is considered safe.

    Raises:
        TypeError: If query is not a string.
        ValueError: If the query is empty or blank.
        UnsafeSQLError: If the query contains forbidden operations or
            references tables/columns outside the whitelists.
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

    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        raise UnsafeSQLError("Only SELECT or WITH queries are allowed")

    if allowed_tables is not None:
        referenced = _extract_referenced_tables(upper)
        unknown = referenced - {t.upper() for t in allowed_tables}
        if unknown:
            raise UnsafeSQLError(f"Unknown table(s): {', '.join(sorted(unknown))}")

    if allowed_columns is not None:
        referenced = _extract_referenced_columns(upper)
        unknown = referenced - {c.upper() for c in allowed_columns}
        if unknown:
            raise UnsafeSQLError(f"Unknown column(s): {', '.join(sorted(unknown))}")

    return query
