"""Tests for whatsmyname.orchestrator — input detection, parsing, and report logic."""

from whatsmyname.orchestrator import (
    Finding,
    InputType,
    UnifiedReport,
    detect_input_type,
    email_variants,
    parse_phone,
)


# ---------------------------------------------------------------------------
# detect_input_type
# ---------------------------------------------------------------------------


class TestDetectInputType:
    def test_username_plain(self):
        assert detect_input_type("johndoe") == InputType.USERNAME

    def test_username_with_dots(self):
        assert detect_input_type("john.doe") == InputType.USERNAME

    def test_email_simple(self):
        assert detect_input_type("john@example.com") == InputType.EMAIL

    def test_email_with_plus(self):
        assert detect_input_type("john+tag@gmail.com") == InputType.EMAIL

    def test_phone_us(self):
        assert detect_input_type("+15551234567") == InputType.PHONE

    def test_phone_international(self):
        assert detect_input_type("+44 20 7946 0958") == InputType.PHONE

    def test_phone_with_dashes(self):
        assert detect_input_type("555-123-4567") == InputType.PHONE

    def test_phone_with_parens(self):
        assert detect_input_type("(555) 123-4567") == InputType.PHONE

    def test_whitespace_stripped(self):
        assert detect_input_type("  johndoe  ") == InputType.USERNAME


# ---------------------------------------------------------------------------
# parse_phone
# ---------------------------------------------------------------------------


class TestParsePhone:
    def test_us_number_with_plus(self):
        cc, num = parse_phone("+15551234567")
        assert cc == "+1"
        assert num == "5551234567"

    def test_uk_number(self):
        cc, num = parse_phone("+442079460958")
        assert cc == "+44"
        assert num == "2079460958"

    def test_no_country_code_defaults_us(self):
        cc, num = parse_phone("5551234567")
        assert cc == "+1"
        assert num == "5551234567"

    def test_strips_formatting(self):
        cc, num = parse_phone("+1 (555) 123-4567")
        assert cc == "+1"
        assert "555" in num


# ---------------------------------------------------------------------------
# email_variants
# ---------------------------------------------------------------------------


class TestEmailVariants:
    def test_returns_list(self):
        result = email_variants("johndoe")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_includes_gmail(self):
        result = email_variants("johndoe")
        assert "johndoe@gmail.com" in result

    def test_includes_common_domains(self):
        result = email_variants("testuser")
        domains = [v.split("@")[1] for v in result]
        assert "gmail.com" in domains
        assert "yahoo.com" in domains
        assert "outlook.com" in domains


# ---------------------------------------------------------------------------
# UnifiedReport
# ---------------------------------------------------------------------------


class TestUnifiedReport:
    def _make_report(self, findings=None):
        return UnifiedReport(
            target="johndoe",
            input_type="username",
            timestamp="2026-01-01T00:00:00Z",
            all_findings=findings or [],
        )

    def test_empty_report(self):
        r = self._make_report()
        assert r.found_count == 0
        assert r.unique_urls == set()
        assert r.by_category() == {}

    def test_found_count(self):
        findings = [
            Finding(source_tool="wmn", site_name="GitHub", url="https://github.com/johndoe"),
            Finding(source_tool="sherlock", site_name="Twitter", url="https://twitter.com/johndoe"),
        ]
        r = self._make_report(findings)
        assert r.found_count == 2

    def test_unique_urls_deduplicates(self):
        findings = [
            Finding(source_tool="wmn", site_name="GitHub", url="https://github.com/johndoe"),
            Finding(source_tool="sherlock", site_name="GitHub", url="https://github.com/johndoe"),
        ]
        r = self._make_report(findings)
        assert r.found_count == 1

    def test_by_category(self):
        findings = [
            Finding(source_tool="wmn", site_name="GitHub", url="https://github.com/a", category="coding"),
            Finding(source_tool="wmn", site_name="Reddit", url="https://reddit.com/a", category="social"),
            Finding(source_tool="wmn", site_name="Twitter", url="https://twitter.com/a", category="social"),
        ]
        r = self._make_report(findings)
        cats = r.by_category()
        assert len(cats["social"]) == 2
        assert len(cats["coding"]) == 1

    def test_by_tool(self):
        findings = [
            Finding(source_tool="wmn", site_name="GitHub", url="https://github.com/a"),
            Finding(source_tool="sherlock", site_name="Twitter", url="https://twitter.com/a"),
        ]
        r = self._make_report(findings)
        tools = r.by_tool()
        assert "wmn" in tools
        assert "sherlock" in tools

    def test_deduplicated_findings(self):
        findings = [
            Finding(source_tool="wmn", site_name="GitHub", url="https://github.com/johndoe"),
            Finding(source_tool="sherlock", site_name="GitHub", url="https://github.com/johndoe/"),
        ]
        r = self._make_report(findings)
        deduped = r.deduplicated_findings()
        assert len(deduped) == 1
