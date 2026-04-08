"""Tests for empty catches detector."""

from debtx.detectors.empty_catches import EmptyCatchesDetector
from debtx.languages import FileContext


def _make_py_context(code: str) -> FileContext:
    return FileContext(
        path="test.py",
        language_name="python",
        lines=tuple(code.splitlines()),
        functions=(),
        imports=(),
    )


def _make_ts_context(code: str) -> FileContext:
    return FileContext(
        path="test.ts",
        language_name="typescript",
        lines=tuple(code.splitlines()),
        functions=(),
        imports=(),
    )


def test_detects_python_empty_except():
    code = "try:\n    x = 1\nexcept Exception:\n    pass"
    ctx = _make_py_context(code)
    findings = EmptyCatchesDetector().detect(ctx)
    assert len(findings) == 1


def test_ignores_python_except_with_body():
    code = "try:\n    x = 1\nexcept Exception as e:\n    logger.error(e)"
    ctx = _make_py_context(code)
    findings = EmptyCatchesDetector().detect(ctx)
    assert len(findings) == 0


def test_detects_ts_empty_catch():
    code = "try {\n  x = 1;\n} catch (e) {}"
    ctx = _make_ts_context(code)
    findings = EmptyCatchesDetector().detect(ctx)
    assert len(findings) == 1
