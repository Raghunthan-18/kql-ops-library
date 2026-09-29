#!/usr/bin/env python3
"""Regenerates the query index table in README.md from the file headers."""
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent.parent
rows = []
for path in sorted(root.rglob("*.kql")):
    if ".git" in path.parts:
        continue
    head = {m.group(1): m.group(2).strip() for m in re.finditer(r"^// ([\w ]+): (.*)$", path.read_text(), re.M)}
    rel = path.relative_to(root).as_posix()
    area = rel.split("/")[1]
    rows.append(f"| {area} | [{head['Title']}]({rel}) | {head['Source']} | {head['When to use']} |")

table = "| Area | Query | Run in | When to use |\n|---|---|---|---|\n" + "\n".join(rows)
readme = root / "README.md"
text = readme.read_text()
text = re.sub(r"<!-- index:start -->.*<!-- index:end -->",
              f"<!-- index:start -->\n{table}\n<!-- index:end -->", text, flags=re.S)
readme.write_text(text)
print(f"indexed {len(rows)} queries")
