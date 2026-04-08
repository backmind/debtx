"""TypeScript/JavaScript language implementation for file parsing."""

from __future__ import annotations

import re

from debtx.languages import FileContext, register_language
from debtx.models import FunctionSpan, ImportInfo

_FUNC_PATTERNS = [
    re.compile(r"^(\s*)(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\("),
    re.compile(r"^(\s*)(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\("),
    re.compile(r"^(\s*)(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function"),
    re.compile(r"^(\s*)(?:public|private|protected|static|\s)*(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*\w[^{]*)?\{"),
]

_IMPORT_RE = re.compile(r"""^\s*import\s+(?:\{([^}]+)\}|(\w+))\s+from\s+['"]([^'"]+)['"]""")
_REQUIRE_RE = re.compile(r"""^\s*(?:const|let|var)\s+(?:\{([^}]+)\}|(\w+))\s*=\s*require\(\s*['"]([^'"]+)['"]\s*\)""")

_SNAKE = re.compile(r"^[a-z_][a-z0-9_]*$")
_CAMEL = re.compile(r"^[a-z][a-zA-Z0-9]*$")
_PASCAL = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
_UPPER = re.compile(r"^[A-Z][A-Z0-9_]*$")


class TypeScriptLanguage:
    @property
    def name(self) -> str:
        return "typescript"

    @property
    def extensions(self) -> tuple[str, ...]:
        return (".ts", ".tsx", ".js", ".jsx")

    def is_comment(self, line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*")

    def is_import(self, line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith("import ") or "require(" in stripped

    def get_function_boundaries(self, lines: tuple[str, ...]) -> tuple[FunctionSpan, ...]:
        functions: list[FunctionSpan] = []

        for i, line in enumerate(lines):
            match = None
            for pattern in _FUNC_PATTERNS:
                match = pattern.match(line)
                if match:
                    break

            if not match:
                continue

            indent = len(match.group(1))
            func_name = match.group(2)
            start = i

            brace_count = 0
            found_opening = False
            end = start

            for j in range(i, len(lines)):
                for ch in lines[j]:
                    if ch == "{":
                        brace_count += 1
                        found_opening = True
                    elif ch == "}":
                        brace_count -= 1

                if found_opening and brace_count <= 0:
                    end = j
                    break
            else:
                end = len(lines) - 1

            if end == start:
                end = start + 1

            functions.append(FunctionSpan(name=func_name, start=start, end=end, indent=indent))

        return tuple(functions)

    def get_indent_level(self, line: str) -> int:
        if not line.strip():
            return 0
        spaces = len(line) - len(line.lstrip())
        return spaces // 2

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

            match = _IMPORT_RE.match(stripped)
            if match:
                named = match.group(1)
                default = match.group(2)
                module = match.group(3)

                names: list[str] = []
                if named:
                    for part in named.split(","):
                        part = part.strip()
                        if not part:
                            continue
                        if " as " in part:
                            names.append(part.split(" as ")[-1].strip())
                        else:
                            names.append(part.strip())
                elif default:
                    names.append(default)

                imports.append(ImportInfo(module=module, names=tuple(names), line=i))
                continue

            match = _REQUIRE_RE.match(stripped)
            if match:
                named = match.group(1)
                default = match.group(2)
                module = match.group(3)

                names = []
                if named:
                    for part in named.split(","):
                        part = part.strip()
                        if part:
                            names.append(part.strip())
                elif default:
                    names.append(default)

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


_instance = TypeScriptLanguage()
register_language(_instance)
