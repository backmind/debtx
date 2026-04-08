"""Python language implementation for file parsing."""

from __future__ import annotations

import re

from debtx.languages import FileContext, register_language
from debtx.models import FunctionSpan, ImportInfo

_FUNC_RE = re.compile(r"^(\s*)(async\s+)?def\s+(\w+)\s*\(")
_IMPORT_RE = re.compile(r"^\s*(?:from\s+([\w.]+)\s+)?import\s+(.+)")
_SNAKE = re.compile(r"^[a-z_][a-z0-9_]*$")
_CAMEL = re.compile(r"^[a-z][a-zA-Z0-9]*$")
_PASCAL = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
_UPPER = re.compile(r"^[A-Z][A-Z0-9_]*$")


class PythonLanguage:
    @property
    def name(self) -> str:
        return "python"

    @property
    def extensions(self) -> tuple[str, ...]:
        return (".py",)

    def is_comment(self, line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith("#")

    def is_import(self, line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith("import ") or stripped.startswith("from ")

    def get_function_boundaries(self, lines: tuple[str, ...]) -> tuple[FunctionSpan, ...]:
        functions: list[FunctionSpan] = []

        for i, line in enumerate(lines):
            match = _FUNC_RE.match(line)
            if not match:
                continue

            indent = len(match.group(1))
            func_name = match.group(3)
            start = i
            end = i

            for j in range(i + 1, len(lines)):
                subsequent = lines[j]
                if not subsequent.strip():
                    continue
                if subsequent.strip().startswith("#"):
                    continue
                if subsequent.strip().startswith("@"):
                    continue

                subsequent_indent = len(subsequent) - len(subsequent.lstrip())
                if subsequent_indent <= indent:
                    break
                end = j

            if end == start:
                end = start + 1

            functions.append(FunctionSpan(name=func_name, start=start, end=end, indent=indent))

        return tuple(functions)

    def get_indent_level(self, line: str) -> int:
        if not line.strip():
            return 0
        spaces = len(line) - len(line.lstrip())
        if line[0] == "\t" if line else False:
            tabs = len(line) - len(line.lstrip("\t"))
            return tabs
        return spaces // 4

    def get_naming_convention(self, name: str) -> str:
        if _UPPER.match(name):
            return "UPPER_CASE"
        if _PASCAL.match(name):
            return "PascalCase"
        if _SNAKE.match(name):
            return "snake_case"
        if _CAMEL.match(name):
            return "camelCase"
        return "mixed"

    def parse_imports(self, lines: tuple[str, ...]) -> tuple[ImportInfo, ...]:
        imports: list[ImportInfo] = []

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not (stripped.startswith("import ") or stripped.startswith("from ")):
                continue

            match = _IMPORT_RE.match(stripped)
            if not match:
                continue

            module = match.group(1) or ""
            names_str = match.group(2).strip()

            if names_str.startswith("("):
                names_str = names_str.strip("()")
            names_str = names_str.split("#")[0].strip()

            names: list[str] = []
            for part in names_str.split(","):
                part = part.strip()
                if not part:
                    continue
                if " as " in part:
                    names.append(part.split(" as ")[-1].strip())
                else:
                    names.append(part.split(".")[-1].strip())

            if not module and names:
                module = names[0]
                names = [n for n in names if n != module]
                if not names:
                    names = [module.split(".")[-1]]

            imports.append(ImportInfo(module=module, names=tuple(names), line=i))

        return tuple(imports)

    def parse_file(self, path: str, lines: tuple[str, ...]) -> FileContext:
        return FileContext(
            path=path,
            language_name=self.name,
            lines=lines,
            functions=self.get_function_boundaries(lines),
            imports=self.parse_imports(lines),
        )


_instance = PythonLanguage()
register_language(_instance)
