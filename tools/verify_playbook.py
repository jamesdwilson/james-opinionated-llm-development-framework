#!/usr/bin/env python3
"""Verify the playbook's publication set, citations, and local links."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
LEDGER = ROOT / "research" / "sources.json"
CITATION_RE = re.compile(r"\[\[(\d+)\]\]\((https?://[^)]+)\)")
PLAIN_NUMBER_RE = re.compile(r"(?<!\[)\[(\d+)\](?!\])")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def publication_files() -> set[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
    ).decode()
    return {
        (ROOT / relative).resolve()
        for relative in output.split("\0")
        if relative and (ROOT / relative).is_file()
    }


def validate_ledger(errors: list[str]) -> dict[int, str]:
    ledger = json.loads(LEDGER.read_text())
    entries = ledger.get("sources", [])
    ids = [int(item["id"]) for item in entries]
    urls = [item["url"] for item in entries]

    expected_ids = list(range(1, len(entries) + 1))
    if ids != expected_ids:
        fail(f"source IDs must be sequential: {ids}", errors)
    if len(urls) != len(set(urls)):
        fail("source ledger contains duplicate URLs", errors)

    return {int(item["id"]): item["url"] for item in entries}


def validate_citations(files: set[Path], sources: dict[int, str], errors: list[str]) -> None:
    readme_seen: set[int] = set()

    for markdown in sorted(path for path in files if path.suffix.lower() == ".md"):
        text = markdown.read_text()
        relative = markdown.relative_to(ROOT)

        for match in CITATION_RE.finditer(text):
            source_id = int(match.group(1))
            url = match.group(2)
            if markdown == README:
                readme_seen.add(source_id)
            expected = sources.get(source_id)
            if expected is None:
                fail(f"{relative} cites unknown source [{source_id}]", errors)
            elif expected != url:
                fail(
                    f"{relative} source [{source_id}] URL differs from ledger: {url} != {expected}",
                    errors,
                )

        for match in PLAIN_NUMBER_RE.finditer(text):
            fail(f"{relative} contains a non-hyperlinked numeric citation [{match.group(1)}]", errors)

    missing = sorted(set(sources) - readme_seen)
    if missing:
        fail(f"README omits ledger sources: {missing}", errors)


def validate_local_links(files: set[Path], errors: list[str]) -> None:
    published_dirs = {
        parent
        for path in files
        for parent in path.parents
        if parent == ROOT or ROOT in parent.parents
    }

    for markdown in sorted(path for path in files if path.suffix.lower() == ".md"):
        text = markdown.read_text()
        relative_path = markdown.relative_to(ROOT)
        for target in MARKDOWN_LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = target.split("#", 1)[0]
            if not relative:
                continue
            destination = (markdown.parent / relative).resolve()
            if destination not in files and destination not in published_dirs:
                fail(f"{relative_path} links outside the publication set: {target}", errors)


def main() -> int:
    errors: list[str] = []
    files = publication_files()
    sources = validate_ledger(errors)
    validate_citations(files, sources, errors)
    validate_local_links(files, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAILED: {len(errors)} issue(s)")
        return 1

    print(f"PASS: publication set contains {len(files)} files")
    print("PASS: citations are hyperlinked and match the ledger")
    print("PASS: local Markdown links stay inside the publication set")
    return 0


if __name__ == "__main__":
    sys.exit(main())
