"""Tests for giant functions detector."""

from debtx.detectors.giant_functions import GiantFunctionsDetector
from debtx.languages import FileContext
from debtx.models import FunctionSpan


def _make_context(functions: tuple[FunctionSpan, ...]) -> FileContext:
    return FileContext(
        path="test.py",
        language_name="python",
        lines=("",) * 200,
        functions=functions,
        imports=(),
    )


def test_detects_giant_function():
    funcs = (FunctionSpan(name="big_func", start=0, end=120, indent=0),)
    ctx = _make_context(funcs)
    findings = GiantFunctionsDetector().detect(ctx)
    assert len(findings) == 1
    assert "big_func" in findings[0].message
    assert "121" in findings[0].message


def test_ignores_small_function():
    funcs = (FunctionSpan(name="small_func", start=0, end=20, indent=0),)
    ctx = _make_context(funcs)
    findings = GiantFunctionsDetector().detect(ctx)
    assert len(findings) == 0


def test_strict_mode_lower_threshold():
    funcs = (FunctionSpan(name="medium_func", start=0, end=60, indent=0),)
    ctx = _make_context(funcs)
    normal = GiantFunctionsDetector().detect(ctx, strict=False)
    strict = GiantFunctionsDetector().detect(ctx, strict=True)
    assert len(normal) == 0
    assert len(strict) == 1
