#!/usr/bin/env python3
"""
No-PII Repository Guardrail Scanner (`scripts/check_no_pii.py`)
===============================================================
Enforces the project rule that NO Personal Identifiable Information (PII) is
persisted or committed in tracked repository files. Whenever examples, defaults,
or test fixtures are needed, only approved generic mocks may be used.

Usage:
    python3 scripts/check_no_pii.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Canonical whitelist of allowed generic mock names and dates in repo examples/tests
ALLOWED_MOCK_NAMES = {
    "",
    "JOHN DOE",
    "JANE DOE",
    "TEST USER",
    "LUCKY ONE",
    "GEMINI ENGINE",
    "GEMINI USER",
    "TREVO DA SORTE",
    "LOTTERY",
    "[REDACTED PII]",
}

ALLOWED_MOCK_BIRTH_DATES = {
    "1970-01-01",
    "1980-01-01",
    "1985-05-15",
    "1990-01-01",
    "1990-05-01",
    "1990-06-15",
    "1995-05-15",
    "2000-01-01",
    "2000-04-16",
}

FORBIDDEN_TRACKED_PATTERNS = (
    re.compile(r"\.local\.ya?ml$"),
    re.compile(r"lottery_personal\.toml$"),
    re.compile(r"\.personal\."),
)

YAML_FULL_NAME_RE = re.compile(r"""^\s*full_name\s*:\s*['"]?([^'"#\n]+?)['"]?\s*(?:#.*)?$""", re.MULTILINE)
YAML_BIRTH_DATE_RE = re.compile(r"""^\s*birth_date\s*:\s*['"]?(\d{4}-\d{2}-\d{2})['"]?\s*(?:#.*)?$""", re.MULTILINE)
PY_BIRTH_DATE_DEFAULT_RE = re.compile(r"""birth_date\s*(?::[^=\n]+)?=\s*['"](\d{4}-\d{2}-\d{2})['"]""")
PY_FULL_NAME_DEFAULT_RE = re.compile(r"""full_name\s*(?::\s*(?:str|Optional\[str\]|Annotated\[[^\n]+\]))?\s*=\s*['"]([^'"]+)['"]""")
MD_CALIBRATION_RE = re.compile(r"""(?:\*\*Player Calibration:\*\*|Calibrated to player)\s+([A-Za-zÀ-ÿ ]+?)\s*\((?:born|Birth date:)\s*(\d{4}-\d{2}-\d{2})\)""")


def get_candidate_files(repo_root: Path) -> list[Path]:
    """Return project code, config, test, report, and rule files to scan (excluding 3rd-party skill bundles)."""
    files: list[Path] = []
    for extra_dir in ("engine", "tests", "cockpit", "desktop", "docs/agents", ".agents/rules", "reports", "scripts"):
        base = repo_root / extra_dir
        if base.exists():
            files.extend(
                p
                for p in base.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts
            )

    for ext in ("*.yaml", "*.yml", "*.toml", "*.md", "*.py"):
        files.extend(p for p in repo_root.glob(ext) if p.is_file())

    seen = set()
    unique: list[Path] = []
    for f in files:
        if f.exists() and str(f) not in seen:
            seen.add(str(f))
            unique.append(f)
    return unique


def scan_repository(repo_root: Path | None = None) -> list[str]:
    root = (repo_root or Path(__file__).resolve().parent.parent).resolve()
    violations: list[str] = []

    # 1. Check git-tracked files for forbidden local/personal files
    try:
        tracked = subprocess.check_output(
            ["git", "ls-files"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).splitlines()
        for rel in tracked:
            for pat in FORBIDDEN_TRACKED_PATTERNS:
                if pat.search(rel):
                    violations.append(f"Forbidden local/PII file is tracked by git: {rel}")
    except Exception:
        pass

    # 2. Scan code, configs, tests, and reports for non-mock full_name / birth_date literals
    for file_path in get_candidate_files(root):
        rel_path = file_path.relative_to(root).as_posix()
        if any(part in {".git", "__pycache__", "node_modules", ".venv", "venv"} for part in file_path.parts):
            continue
        if file_path.suffix.lower() not in {".py", ".yaml", ".yml", ".toml", ".md"}:
            continue
        if ".local." in file_path.name:
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            continue

        if file_path.suffix.lower() in {".yaml", ".yml"}:
            for m in YAML_FULL_NAME_RE.finditer(content):
                val = m.group(1).strip().upper()
                if val not in ALLOWED_MOCK_NAMES:
                    violations.append(
                        f"{rel_path}: Non-mock YAML full_name='{m.group(1).strip()}' (use generic mock like 'JANE DOE' or 'JOHN DOE')"
                    )
            for m in YAML_BIRTH_DATE_RE.finditer(content):
                val = m.group(1).strip()
                if val not in ALLOWED_MOCK_BIRTH_DATES:
                    violations.append(
                        f"{rel_path}: Non-mock YAML birth_date='{val}' (use generic mock like '1990-01-01')"
                    )

        if file_path.suffix.lower() == ".md":
            for m in MD_CALIBRATION_RE.finditer(content):
                p_name = m.group(1).strip().upper()
                p_date = m.group(2).strip()
                if p_name not in ALLOWED_MOCK_NAMES or p_date not in ALLOWED_MOCK_BIRTH_DATES:
                    violations.append(
                        f"{rel_path}: Non-mock Markdown player calibration ({m.group(1).strip()}, {p_date})"
                    )

        if file_path.suffix.lower() == ".py" and rel_path != "scripts/check_no_pii.py" and "jota_silva" not in rel_path:
            for m in PY_BIRTH_DATE_DEFAULT_RE.finditer(content):
                val = m.group(1).strip()
                if val not in ALLOWED_MOCK_BIRTH_DATES:
                    violations.append(
                        f"{rel_path}: Non-mock Python birth_date='{val}' (allowed mocks: {sorted(ALLOWED_MOCK_BIRTH_DATES)})"
                    )
            for m in PY_FULL_NAME_DEFAULT_RE.finditer(content):
                val = m.group(1).strip().upper()
                if val not in ALLOWED_MOCK_NAMES and not val.startswith("{"):
                    violations.append(
                        f"{rel_path}: Non-mock Python full_name='{m.group(1).strip()}' (allowed mocks: {sorted(ALLOWED_MOCK_NAMES)})"
                    )

    return violations


def main() -> int:
    violations = scan_repository()
    if violations:
        print("❌ PII Guardrail Check FAILED — found non-mock PII or forbidden tracked files:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1
    print("✅ PII Guardrail Check PASSED — only generic mock examples are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
