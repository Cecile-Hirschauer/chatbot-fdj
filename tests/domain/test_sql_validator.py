import pytest

from chatbot_fdj.domain.sql_validator import UnsafeSQLError, validate_sql


class TestHappyPath:
    def test_simple_select_returns_query(self):
        query = "SELECT * FROM draws"
        assert validate_sql(query) == query

    def test_select_with_where_clause(self):
        query = "SELECT id, date FROM draws WHERE year = 2024"
        assert validate_sql(query) == query

    def test_select_with_join(self):
        query = "SELECT d.id, r.rank FROM draws d JOIN results r ON d.id = r.draw_id"
        assert validate_sql(query) == query

    def test_select_with_aggregate(self):
        query = "SELECT COUNT(*) FROM draws WHERE jackpot > 1000000"
        assert validate_sql(query) == query

    def test_select_case_insensitive(self):
        query = "select * from draws"
        assert validate_sql(query) == query


class TestForbiddenDmlKeywords:
    def test_drop_table_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("DROP TABLE draws")

    def test_drop_database_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("DROP DATABASE lottery")

    def test_delete_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("DELETE FROM draws WHERE id = 1")

    def test_insert_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("INSERT INTO draws VALUES (1, 2, 3)")

    def test_update_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("UPDATE draws SET col = 1")

    def test_truncate_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("TRUNCATE TABLE draws")

    def test_create_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("CREATE TABLE evil (id INT)")

    def test_alter_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("ALTER TABLE draws ADD COLUMN x INT")


class TestForbiddenKeywordsAreCaseInsensitive:
    def test_drop_lowercase_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("drop table draws")

    def test_delete_mixed_case_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("DeLeTe FROM draws")

    def test_insert_uppercase_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("INSERT INTO draws VALUES (1)")


class TestMultipleStatements:
    def test_two_selects_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("SELECT * FROM draws; SELECT * FROM results")

    def test_select_then_drop_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("SELECT * FROM draws; DROP TABLE draws")

    def test_select_with_injected_delete_raises(self):
        with pytest.raises(UnsafeSQLError):
            validate_sql("SELECT * FROM draws; DELETE FROM draws")


class TestInvalidInput:
    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            validate_sql("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            validate_sql("   ")

    def test_non_string_raises(self):
        with pytest.raises(TypeError):
            validate_sql(None)  # type: ignore[arg-type]
