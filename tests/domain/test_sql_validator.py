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


_TABLES = frozenset({"draws", "results"})
_COLUMNS = frozenset({"id", "date", "rank", "jackpot", "draw_id", "year"})


class TestTableWhitelist:
    def test_allowed_table_passes(self):
        query = "SELECT * FROM draws"
        assert validate_sql(query, allowed_tables=_TABLES) == query

    def test_unknown_table_raises(self):
        with pytest.raises(UnsafeSQLError, match="Unknown table"):
            validate_sql("SELECT * FROM users", allowed_tables=_TABLES)

    def test_joined_table_must_be_in_whitelist(self):
        with pytest.raises(UnsafeSQLError, match="Unknown table"):
            validate_sql(
                "SELECT * FROM draws JOIN secrets ON draws.id = secrets.id",
                allowed_tables=_TABLES,
            )

    def test_both_joined_tables_allowed_passes(self):
        query = "SELECT * FROM draws JOIN results ON draws.id = results.draw_id"
        assert validate_sql(query, allowed_tables=_TABLES) == query

    def test_no_whitelist_skips_table_check(self):
        # Without a whitelist any table name is accepted
        assert validate_sql("SELECT * FROM internal_config") is not None


class TestColumnWhitelist:
    def test_allowed_columns_pass(self):
        query = "SELECT id, date FROM draws"
        assert validate_sql(query, allowed_columns=_COLUMNS) == query

    def test_unknown_column_raises(self):
        with pytest.raises(UnsafeSQLError, match="Unknown column"):
            validate_sql("SELECT secret_hash FROM draws", allowed_columns=_COLUMNS)

    def test_wildcard_select_always_passes(self):
        # SELECT * does not enumerate columns, so the whitelist is not applied
        query = "SELECT * FROM draws"
        assert validate_sql(query, allowed_columns=_COLUMNS) == query

    def test_table_qualified_column_passes(self):
        query = (
            "SELECT draws.id, results.rank FROM draws JOIN results ON draws.id = results.draw_id"
        )
        assert validate_sql(query, allowed_columns=_COLUMNS) == query

    def test_aggregate_on_allowed_column_passes(self):
        query = "SELECT COUNT(id) FROM draws"
        assert validate_sql(query, allowed_columns=_COLUMNS) == query

    def test_aggregate_on_unknown_column_raises(self):
        with pytest.raises(UnsafeSQLError, match="Unknown column"):
            validate_sql("SELECT COUNT(password) FROM draws", allowed_columns=_COLUMNS)

    def test_both_whitelists_together(self):
        query = "SELECT id, rank FROM draws JOIN results ON draws.id = results.draw_id"
        assert validate_sql(query, allowed_tables=_TABLES, allowed_columns=_COLUMNS) == query


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
