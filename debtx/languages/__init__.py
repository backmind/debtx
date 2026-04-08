"""Language abstraction layer for multi-language file parsing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from debtx.models import FunctionSpan, ImportInfo


@dataclass(frozen=True)
class FileContext:
    path: str
    language_name: str
    lines: tuple[str, ...]
    functions: tuple[FunctionSpan, ...]
    imports: tuple[ImportInfo, ...]


@runtime_checkable
class Language(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def extensions(self) -> tuple[str, ...]: ...

    def is_comment(self, line: str) -> bool: ...

    def is_import(self, line: str) -> bool: ...

    def get_function_boundaries(self, lines: tuple[str, ...]) -> tuple[FunctionSpan, ...]: ...

    def get_indent_level(self, line: str) -> int: ...

    def get_naming_convention(self, name: str) -> str: ...

    def parse_imports(self, lines: tuple[str, ...]) -> tuple[ImportInfo, ...]: ...

    def parse_file(self, path: str, lines: tuple[str, ...]) -> FileContext: ...


_LANGUAGES: list[Language] = []


def register_language(lang: Language) -> None:
    _LANGUAGES.append(lang)


def get_language(path: str) -> Language | None:
    for lang in _LANGUAGES:
        for ext in lang.extensions:
            if path.endswith(ext):
                return lang
    return None


def get_all_extensions() -> set[str]:
    result: set[str] = set()
    for lang in _LANGUAGES:
        result.update(lang.extensions)
    return result
