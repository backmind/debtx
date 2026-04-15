"""Regression tests for false-positive fixes in hardcoded_values and missing_error_handling."""

from debtx.detectors.dead_code import DeadCodeDetector
from debtx.detectors.hardcoded_values import HardcodedValuesDetector
from debtx.detectors.missing_error_handling import MissingErrorHandlingDetector
from debtx.detectors.todo_comments import TodoCommentsDetector
from debtx.languages.python_lang import PythonLanguage
from debtx.languages.typescript_lang import TypeScriptLanguage


def _py_ctx(source: str):
    lines = tuple(source.splitlines())
    return PythonLanguage().parse_file("src/app.py", lines)


def _ts_ctx(source: str):
    lines = tuple(source.splitlines())
    return TypeScriptLanguage().parse_file("src/app.ts", lines)


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


def test_todo_marker_in_string_literal_ignored():
    src = '''def contract():
    methods = ["CreateTodo(ctx context.Context, todo domain.Todo)"]
    return methods
'''
    findings = TodoCommentsDetector().detect(_py_ctx(src))
    assert findings == ()


def test_todo_lowercase_word_in_code_ignored():
    src = '''def handler():
    todo = fetch_todo()
    return todo
'''
    findings = TodoCommentsDetector().detect(_py_ctx(src))
    assert findings == ()


def test_todo_word_substring_ignored():
    src = '''def f():
    client = connect("Todoist")
    return client
'''
    findings = TodoCommentsDetector().detect(_py_ctx(src))
    assert findings == ()


def test_todo_in_comment_still_detected():
    src = '''def f():
    # TODO: refactor this
    return 1
'''
    findings = TodoCommentsDetector().detect(_py_ctx(src))
    assert any(f.message.startswith("TODO comment") for f in findings)


def test_fixme_in_ts_comment_still_detected():
    src = """function f() {
    // FIXME: handle error
    return 1;
}
"""
    findings = TodoCommentsDetector().detect(_ts_ctx(src))
    assert any(f.message.startswith("FIXME comment") for f in findings)


def test_temp_no_longer_default_marker():
    src = '''def f():
    # Create a temp worktree
    return 1
'''
    findings = TodoCommentsDetector().detect(_py_ctx(src))
    assert findings == ()


def test_dead_code_ignores_trailing_comment_py():
    src = '''def f():
    return clean_up()
    # eslint-disable-next-line-equivalent
'''
    findings = DeadCodeDetector().detect(_py_ctx(src))
    assert findings == ()


def test_dead_code_ignores_trailing_comment_ts():
    src = """function useHook() {
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
}
"""
    findings = DeadCodeDetector().detect(_ts_ctx(src))
    assert findings == ()


def test_dead_code_still_detects_real_unreachable():
    src = '''def f():
    return 1
    x = 2
'''
    findings = DeadCodeDetector().detect(_py_ctx(src))
    assert any("Unreachable" in f.message for f in findings)
