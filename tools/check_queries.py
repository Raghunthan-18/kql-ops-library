#!/usr/bin/env python3
"""Fails CI if any .kql file is missing its documentation header.

Every query must say what it is, where to run it, which tables it needs and
when to reach for it. A query nobody can find or understand is not in the library.
"""
import pathlib
import re
import sys

REQUIRED = ["// Title:", "// Source:", "// Tables:", "// When to use:"]
SOURCES = {"Log Analytics", "Resource Graph"}

root = pathlib.Path(__file__).resolve().parent.parent
errors = []
files = sorted(p for p in root.rglob("*.kql") if ".git" not in p.parts)

for path in files:
    text = path.read_text(encoding="utf-8")
    header = [l for l in text.splitlines() if l.startswith("//")]
    rel = path.relative_to(root)
    for field in REQUIRED:
        if not any(l.startswith(field) for l in header):
            errors.append(f"{rel}: missing '{field}'")
    src = next((l.split(":", 1)[1].strip() for l in header if l.startswith("// Source:")), None)
    if src and src not in SOURCES:
        errors.append(f"{rel}: Source must be one of {sorted(SOURCES)}, got '{src}'")
    body = "\n".join(l for l in text.splitlines() if not l.startswith("//")).strip()
    if not body:
        errors.append(f"{rel}: no query body")
    # Count parentheses outside string literals (regexes inside strings contain them legitimately).
    code = re.sub(r'@?"(?:[^"\\]|\\.)*"|@?\'(?:[^\'\\]|\\.)*\'', '""', body)
    if code.count("(") != code.count(")"):
        errors.append(f"{rel}: unbalanced parentheses")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"{len(files)} queries OK")
