"""Tests for whatsmyname.templates — scan template definitions."""

from whatsmyname.templates import TEMPLATES, get_template, list_templates


class TestGetTemplate:
    def test_existing_template(self):
        t = get_template("quick-check")
        assert t is not None
        assert t.name == "quick-check"
        assert t.quick is True

    def test_case_insensitive(self):
        assert get_template("Quick-Check") is not None

    def test_nonexistent(self):
        assert get_template("nonexistent-template") is None

    def test_full_osint_has_deep(self):
        t = get_template("full-osint")
        assert t is not None
        assert t.deep is True
        assert t.timeout_multiplier == 2.0

    def test_passive_only_flag(self):
        t = get_template("passive-only")
        assert t is not None
        assert t.passive_only is True


class TestListTemplates:
    def test_returns_all(self):
        templates = list_templates()
        assert len(templates) == len(TEMPLATES)

    def test_template_has_required_keys(self):
        templates = list_templates()
        for t in templates:
            assert "name" in t
            assert "description" in t
            assert "tools" in t
            assert "tags" in t

    def test_all_templates_have_tags(self):
        for t in TEMPLATES.values():
            assert len(t.tags) > 0, f"Template '{t.name}' has no tags"
