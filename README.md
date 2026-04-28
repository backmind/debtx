# debtx

AI-generated code debt scanner. Grade your codebase A-F.

## Install

This fork is not on PyPI. Install from git:

```bash
pip install "debtx @ git+https://github.com/backmind/debtx@main"
```

## Quick start

```bash
debtx scan .
debtx scan ./src --format md
debtx scan . --fail-under B
```

## Usage

`debtx scan [PATH]` runs the scan and prints a graded report. Flags:

- `--format {terminal,md,json}` — output format. `terminal` is a Rich
  table, `md` a Markdown report, `json` the machine-readable schema
  documented below.
- `--lang {python,typescript,all}` — filter discovery to one language.
  Default `all`.
- `--strict` — apply stricter thresholds and re-weight categories.
  Lowers scores on the same findings.
- `--exclude PATTERN` — glob (relative to scan root) to skip. Repeatable.
- `--output PATH`, `-o PATH` — write the report to a file instead of
  stdout. Used with `--format md` or `--format json`.
- `--fail-under {A,B,C,D,F}` — exit non-zero if the overall grade is
  worse than this threshold. Default: never fail (exit 0 regardless).
  Use this to opt into gating; debtx is informative-only by default.

`debtx badge [PATH] -o badge.svg` generates an SVG badge with the grade.

## CI integration

debtx is informative by default. It produces a grade, never an exit
code, unless you opt into `--fail-under`. This is intentional: debtx is
one signal among several, never the source of truth on code quality.
Treat the grade as a trend.

> **Anti-pattern.** Do not promote debtx to a required check on its
> own. Pair it with at least one other orthogonal signal (lint, tests,
> type-check) and treat the grade as a trend, not a gate.

### GitHub Actions composite

A reusable composite action lives at `.github/actions/scan`:

```yaml
- uses: actions/checkout@v4
- uses: backmind/debtx/.github/actions/scan@main
  with:
    path: .
    language: python
    # fail-under: ''   # leave empty for informative mode (recommended)
```

Inputs: `path`, `language`, `strict`, `fail-under` (empty by default),
`python-version`. See `.github/actions/scan/action.yml` for defaults.

### Inline alternative

If you'd rather not depend on a third-party composite, the same flow
in six lines of `run:`:

```yaml
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
- run: pip install "debtx @ git+https://github.com/backmind/debtx@main"
- run: debtx scan . --format json --output debtx-report.json
- uses: actions/upload-artifact@v4
  with:
    name: debtx-report
    path: debtx-report.json
```

### What you get in the PR view

Either path produces two artifacts: a **job summary** (Markdown table
with overall grade, vibe score, per-category breakdown) visible on the
run page, and a **`debtx-report.json` artifact** suitable for
programmatic post-processing.

## Output formats

### terminal

A coloured Rich table with the overall grade, vibe score, per-category
breakdown, and a tail of representative findings.

### md

A self-contained Markdown report (`# debtx Report` header, summary
table, per-category sections). Pipe with `-o REPORT.md` to save.

### json

Machine-readable. The fields below form the stable contract for CI
integrations:

| Field | Type | Notes |
|-------|------|-------|
| `overall_grade` | string | `A` / `B` / `C` / `D` / `F` |
| `vibe_score` | int | 0–100 |
| `files_scanned` | int | After exclude filters |
| `total_lines` | int | Sum across scanned files |
| `category_scores[]` | array | One entry per detector |
| `category_scores[].name` | string | Human label |
| `category_scores[].grade` | string | A–F for that category |
| `category_scores[].score` | float | 0–100 |
| `category_scores[].finding_count` | int | Findings in this category |
| `category_scores[].weight` | float | Weighting in vibe score |

`path`, `timestamp`, `summary_line`, `file_reports`, and
`category_scores[].detector_id` are also emitted but less stable.

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

## Inline ignore directives

Suppress findings on a per-line basis using a comment. Works in `#`
(Python) and `//` (TypeScript) comments. Directives inside string
literals are ignored.

| Form | Effect |
|------|--------|
| `# debtx: ignore` | Ignore all detectors on this line |
| `# debtx: ignore[id1, id2]` | Ignore listed detectors on this line |
| `# debtx: ignore-next-line` | Ignore all detectors on the next line |
| `# debtx: ignore-next-line[id]` | Ignore one detector on the next line |

Detector IDs match `category_scores[].detector_id` in the JSON output
(e.g. `dead_code`, `empty_catches`, `hardcoded_values`).

```python
try:
    do_thing()
except Exception:  # debtx: ignore[empty_catches]
    pass
```

## License

MIT
