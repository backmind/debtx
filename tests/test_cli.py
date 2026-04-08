"""Tests for CLI commands."""

import os
import tempfile

from click.testing import CliRunner

from debtx.cli import main


def _make_test_project(tmpdir: str) -> None:
    with open(os.path.join(tmpdir, "app.py"), "w") as f:
        f.write("import os\nimport sys\n\ndef hello():\n    print('hello')\n")

    with open(os.path.join(tmpdir, "utils.py"), "w") as f:
        f.write("def add(a, b):\n    return a + b\n")


def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "debtx" in result.output


def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_scan_terminal():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_test_project(tmpdir)
        result = runner.invoke(main, ["scan", tmpdir])
        assert result.exit_code == 0
        assert "debtx" in result.output


def test_scan_json():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_test_project(tmpdir)
        result = runner.invoke(main, ["scan", tmpdir, "--format", "json"])
        assert result.exit_code == 0
        assert '"vibe_score"' in result.output


def test_scan_markdown():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_test_project(tmpdir)
        result = runner.invoke(main, ["scan", tmpdir, "--format", "md"])
        assert result.exit_code == 0
        assert "# debtx Report" in result.output


def test_scan_empty_dir():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        result = runner.invoke(main, ["scan", tmpdir])
        assert result.exit_code == 0


def test_scan_nonexistent_path():
    runner = CliRunner()
    result = runner.invoke(main, ["scan", "/nonexistent/path"])
    assert result.exit_code != 0


def test_scan_with_lang_filter():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_test_project(tmpdir)
        result = runner.invoke(main, ["scan", tmpdir, "--lang", "python"])
        assert result.exit_code == 0


def test_scan_strict():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_test_project(tmpdir)
        result = runner.invoke(main, ["scan", tmpdir, "--strict"])
        assert result.exit_code == 0
