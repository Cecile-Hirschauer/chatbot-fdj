import pytest

from chatbot_fdj.domain.sql_validator import UnsafeSQLError, validate_sql


class TestValidateSql:
    def test_valid_select_returns_query(self):
        query = "SELECT * FROM draws"
        assert validate_sql(query) == query

    def test_empty_query_raises(self):
        with pytest.raises(ValueError):
            validate_sql("")

    def test_drop_table_raises_unsafe(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("DROP TABLE draws")

    def test_delete_raises_unsafe(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("DELETE FROM draws WHERE id = 1")

    def test_insert_raises_unsafe(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("INSERT INTO draws VALUES (1, 2, 3)")

    def test_update_raises_unsafe(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("UPDATE draws SET col = 1")
