# debtx

AI-generated code debt scanner. Grade your codebase A-F.

## Install

```bash
pip install debtx
```

## Usage

```bash
debtx scan .
debtx scan ./src --format md
debtx scan . --strict
debtx badge
```

## What it detects

12 categories of "vibe code" anti-patterns that AI coding agents commonly produce:

| Detector | What it catches |
|----------|----------------|
| Giant Functions | Functions over 100 lines |
| Empty Catches | Silent error swallowing |
| Hardcoded Values | URLs, IPs, secrets, magic numbers |
| Duplicated Blocks | Copy-paste code patterns |
| Missing Error Handling | IO ops without try/except |
| Orphaned Imports | Unused imports |
| No Test Coverage | Source files with no tests |
| Massive Files | Files over 500 lines |
| TODO/FIXME Comments | Unresolved markers |
| Inconsistent Naming | Mixed camelCase/snake_case |
| Deep Nesting | 4+ levels of indentation |
| Dead Code | Unreachable code after return/break |

## Grading Scale

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90-100 | Clean codebase |
| B | 75-89 | Minor issues |
| C | 55-74 | Needs attention |
| D | 35-54 | Significant debt |
| F | 0-34 | Critical debt |

## License

MIT
