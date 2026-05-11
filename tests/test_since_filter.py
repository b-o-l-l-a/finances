"""Unit tests for --since date filtering."""

import datetime
import pytest
from click.testing import CliRunner

from finances.cli import parse_since_date, cli


class TestParseSinceDate:
    def test_valid_date(self):
        assert parse_since_date("2026-04-15") == datetime.date(2026, 4, 15)

    def test_none_returns_none(self):
        assert parse_since_date(None) is None

    def test_empty_string_returns_none(self):
        assert parse_since_date("") is None

    def test_invalid_format_returns_none(self):
        assert parse_since_date("not-a-date") is None

    def test_invalid_month_returns_none(self):
        assert parse_since_date("2026-13-01") is None

    def test_wrong_separator_returns_none(self):
        assert parse_since_date("2026/04/15") is None


class TestManualCategorizeSinceOption:
    def test_invalid_since_exits_cleanly(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["manual-categorize", "--since", "bad-date"])
        assert result.exit_code == 0
        assert "Invalid date format" in result.output

    def test_help_shows_since_option(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["manual-categorize", "--help"])
        assert "--since" in result.output


class TestSyncSinceOption:
    def test_invalid_since_exits_cleanly(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["sync", "--since", "bad-date"])
        assert result.exit_code == 0
        assert "Invalid date format" in result.output

    def test_help_shows_since_option(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["sync", "--help"])
        assert "--since" in result.output
