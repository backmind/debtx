"""Tests for scanner integration."""

import os
import os.path
import tempfile

from debtx import scanner
from debtx.scanner import _discover_files, run_scan


def _make_project(tmpdir: str) -> None:
    with open(os.path.join(tmpdir, "main.py"), "w") as f:
        f.write(
            "import os\nimport json\n\n"
            "def process():\n"
            "    data = open('file.txt').read()\n"
            "    return json.loads(data)\n"
        )

    with open(os.path.join(tmpdir, "big.py"), "w") as f:
        lines = ["def big_func():"] + [f"    x = {i}" for i in range(120)]
        f.write("\n".join(lines))

    os.makedirs(os.path.join(tmpdir, "tests"), exist_ok=True)
    with open(os.path.join(tmpdir, "tests", "test_main.py"), "w") as f:
        f.write("def test_something():\n    assert True\n")


def test_scan_basic():
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_project(tmpdir)
        report = run_scan(tmpdir)
        assert report.files_scanned >= 2
        assert report.total_lines > 0
        assert 0 <= report.vibe_score <= 100
        assert report.overall_grade in ("A", "B", "C", "D", "F")


def test_scan_finds_giant_function():
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_project(tmpdir)
        report = run_scan(tmpdir)

        all_findings = []
        for fr in report.file_reports:
            all_findings.extend(fr.findings)

        giant = [f for f in all_findings if f.detector == "giant_functions"]
        assert len(giant) >= 1


def test_scan_finds_missing_error_handling():
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_project(tmpdir)
        report = run_scan(tmpdir)

        all_findings = []
        for fr in report.file_reports:
            all_findings.extend(fr.findings)

        missing = [f for f in all_findings if f.detector == "missing_error_handling"]
        assert len(missing) >= 1


def test_scan_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        report = run_scan(tmpdir)
        assert report.files_scanned == 0
        assert report.vibe_score == 100
        assert report.overall_grade == "A"


def test_scan_language_filter():
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_project(tmpdir)
        with open(os.path.join(tmpdir, "app.ts"), "w") as f:
            f.write("const x = 1;\n")

        py_report = run_scan(tmpdir, language_filter="python")
        ts_report = run_scan(tmpdir, language_filter="typescript")

        assert py_report.files_scanned >= 2
        assert ts_report.files_scanned >= 1


def test_scan_strict_mode():
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_project(tmpdir)
        normal = run_scan(tmpdir)
        strict = run_scan(tmpdir, strict=True)

        assert strict.vibe_score <= normal.vibe_score


def test_discover_files_skips_pseudopath_relpath_failures(monkeypatch):
    """Simulate the Windows \\\\.\\nul case: relpath blows up on one entry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        good_a = os.path.join(tmpdir, "good_a.py")
        good_b = os.path.join(tmpdir, "good_b.py")
        bad = os.path.join(tmpdir, "bad.py")
        for p in (good_a, good_b, bad):
            with open(p, "w") as f:
                f.write("x = 1\n")

        real_relpath = os.path.relpath

        def fake_relpath(path, start):
            if os.path.basename(path) == "bad.py":
                raise ValueError(
                    "path is on mount '\\\\.\\nul', start on mount 'C:'"
                )
            return real_relpath(path, start)

        monkeypatch.setattr(scanner.os.path, "relpath", fake_relpath)

        files = _discover_files(tmpdir, language_filter=None, exclude_patterns=())

        names = {os.path.basename(f) for f in files}
        assert "good_a.py" in names
        assert "good_b.py" in names
        assert "bad.py" not in names


def test_summary_line_format():
    with tempfile.TemporaryDirectory() as tmpdir:
        _make_project(tmpdir)
        report = run_scan(tmpdir)
        assert "debtx:" in report.summary_line
        assert "Vibe Score:" in report.summary_line
        assert "found" in report.summary_line
