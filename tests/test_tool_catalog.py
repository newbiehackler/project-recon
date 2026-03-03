"""Tests for whatsmyname.tool_catalog — catalog entries and lookups."""

from whatsmyname.tool_catalog import (
    ALL_CATEGORIES,
    TOOL_CATALOG,
    CatalogEntry,
    get_all_entries,
    get_entry,
    get_installed,
    get_suggestions_for,
)


class TestCatalogEntry:
    def test_wmn_exists(self):
        entry = get_entry("wmn")
        assert entry is not None
        assert entry.command == "wmn"

    def test_sherlock_exists(self):
        entry = get_entry("sherlock")
        assert entry is not None
        assert entry.category is not None

    def test_nonexistent_tool(self):
        assert get_entry("nonexistent_tool_xyz") is None

    def test_all_entries_have_required_fields(self):
        for entry in TOOL_CATALOG:
            assert entry.name, f"Entry missing name"
            assert entry.command, f"Entry '{entry.name}' missing command"
            assert entry.category, f"Entry '{entry.name}' missing category"
            assert entry.description, f"Entry '{entry.name}' missing description"
            assert entry.install_hint, f"Entry '{entry.name}' missing install_hint"

    def test_all_categories_valid(self):
        for entry in TOOL_CATALOG:
            assert entry.category in ALL_CATEGORIES, (
                f"Entry '{entry.name}' has unknown category '{entry.category}'"
            )

    def test_get_all_entries(self):
        entries = get_all_entries()
        assert len(entries) == len(TOOL_CATALOG)

    def test_get_installed_returns_list(self):
        installed = get_installed()
        assert isinstance(installed, list)

    def test_suggestions_for_wmn(self):
        suggestions = get_suggestions_for("wmn")
        assert isinstance(suggestions, list)
        # wmn has works_well_with defined
        assert len(suggestions) > 0


class TestCatalogExamples:
    def test_wmn_has_examples(self):
        entry = get_entry("wmn")
        assert entry is not None
        assert len(entry.examples) >= 5

    def test_examples_have_cmd_and_desc(self):
        for entry in TOOL_CATALOG:
            for ex in entry.examples:
                assert "cmd" in ex, f"Example in '{entry.name}' missing 'cmd'"
                assert "desc" in ex, f"Example in '{entry.name}' missing 'desc'"
