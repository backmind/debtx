"""Regression tests for false-positive fixes in hardcoded_values and missing_error_handling."""

from debtx.detectors.hardcoded_values import HardcodedValuesDetector
from debtx.detectors.missing_error_handling import MissingErrorHandlingDetector
from debtx.languages.python_lang import PythonLanguage


def _py_ctx(source: str):
    lines = tuple(source.splitlines())
    return PythonLanguage().parse_file("src/app.py", lines)


def test_hardcoded_url_in_docstring_ignored():
    src = '''def f():
    """See https://api.stripe.com/docs for details."""
    return 1
'''
    findings = HardcodedValuesDetector().detect(_py_ctx(src))
    assert findings == ()


def test_hardcoded_secret_in_docstring_ignored():
    src = '''def f():
    """Example: api_key="abcdefghij1234567890"."""
    return 1
'''
    findings = HardcodedValuesDetector().detect(_py_ctx(src))
    assert findings == ()


def test_hardcoded_url_in_code_still_detected():
    src = '''def f():
    url = "https://api.stripe.com/v1"
    return url
'''
    findings = HardcodedValuesDetector().detect(_py_ctx(src))
    assert any("Hardcoded URL" in f.message for f in findings)


def test_missing_error_handling_ignores_open_in_string():
    src = '''def f():
    msg = "use open() to read the file"
    return msg
'''
    findings = MissingErrorHandlingDetector().detect(_py_ctx(src))
    assert findings == ()


def test_missing_error_handling_ignores_open_in_docstring():
    src = '''def f():
    """Wrapper around open() that handles errors."""
    return 1
'''
    findings = MissingErrorHandlingDetector().detect(_py_ctx(src))
    assert findings == ()


def test_missing_error_handling_still_detects_real_open():
    src = '''def f():
    data = open("config.yaml").read()
    return data
'''
    findings = MissingErrorHandlingDetector().detect(_py_ctx(src))
    assert any("IO operation" in f.message for f in findings)
