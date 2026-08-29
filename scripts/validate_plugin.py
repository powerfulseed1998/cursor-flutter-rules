#!/usr/bin/env python3
"""Validate the Flutter Cursor Rules plugin.

This repository is a Cursor plugin made of documentation/rule files rather than
runnable source code. This script is its "build": it verifies that the plugin
manifest, the rule files, and the README stay consistent so the plugin installs
cleanly in any Cursor project.

Checks performed:
  1. `.cursor-plugin/plugin.json` is valid JSON and has the required fields.
  2. Every `rules/*.mdc` file has valid YAML frontmatter with a non-empty
     `description` and a boolean `alwaysApply`, followed by a non-empty body.
  3. The README rule table references every rule file, and every rule file is
     listed in the README (no orphans, no dangling rows).

Exit code is 0 when everything passes and 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - dependency is expected in the env
    print("ERROR: PyYAML is required. Install it with `pip install pyyaml`.")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_MANIFEST = REPO_ROOT / ".cursor-plugin" / "plugin.json"
RULES_DIR = REPO_ROOT / "rules"
README = REPO_ROOT / "README.md"

REQUIRED_MANIFEST_FIELDS = ("name", "displayName", "version", "description")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


class Reporter:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.checks = 0

    def ok(self, message: str) -> None:
        self.checks += 1
        print(f"  \033[32mPASS\033[0m {message}")

    def fail(self, message: str) -> None:
        self.checks += 1
        self.errors.append(message)
        print(f"  \033[31mFAIL\033[0m {message}")


def validate_manifest(report: Reporter) -> None:
    print("\n[1/3] Plugin manifest")
    if not PLUGIN_MANIFEST.is_file():
        report.fail(f"missing manifest: {PLUGIN_MANIFEST.relative_to(REPO_ROOT)}")
        return
    try:
        data = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        report.fail(f"plugin.json is not valid JSON: {exc}")
        return
    report.ok("plugin.json is valid JSON")

    for field in REQUIRED_MANIFEST_FIELDS:
        value = data.get(field)
        if isinstance(value, str) and value.strip():
            report.ok(f"plugin.json has non-empty `{field}`")
        else:
            report.fail(f"plugin.json missing/empty required field `{field}`")


def parse_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, "", "no `--- ... ---` YAML frontmatter block found"
    raw, body = match.group(1), match.group(2)
    try:
        meta = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        return None, body, f"invalid YAML frontmatter: {exc}"
    if not isinstance(meta, dict):
        return None, body, "frontmatter is not a YAML mapping"
    return meta, body, None


def validate_rules(report: Reporter) -> list[str]:
    print("\n[2/3] Rule files")
    if not RULES_DIR.is_dir():
        report.fail(f"missing rules directory: {RULES_DIR.relative_to(REPO_ROOT)}")
        return []

    rule_files = sorted(RULES_DIR.glob("*.mdc"))
    if not rule_files:
        report.fail("no `.mdc` rule files found in rules/")
        return []

    names: list[str] = []
    for path in rule_files:
        rel = path.relative_to(REPO_ROOT)
        names.append(path.name)
        meta, body, err = parse_frontmatter(path.read_text(encoding="utf-8"))
        if err:
            report.fail(f"{rel}: {err}")
            continue

        description = meta.get("description")
        if isinstance(description, str) and description.strip():
            report.ok(f"{rel}: valid frontmatter + non-empty body"
                      if body.strip() else f"{rel}: has description")
        else:
            report.fail(f"{rel}: missing/empty `description`")

        if "alwaysApply" in meta and not isinstance(meta["alwaysApply"], bool):
            report.fail(f"{rel}: `alwaysApply` must be a boolean")

        if not body.strip():
            report.fail(f"{rel}: body after frontmatter is empty")

    return names


def validate_readme(report: Reporter, rule_names: list[str]) -> None:
    print("\n[3/3] README consistency")
    if not README.is_file():
        report.fail("missing README.md")
        return
    text = README.read_text(encoding="utf-8")
    referenced = set(re.findall(r"rules/([\w-]+\.mdc)", text))

    for name in rule_names:
        if name in referenced:
            report.ok(f"README references rules/{name}")
        else:
            report.fail(f"README does not reference rules/{name}")

    for name in sorted(referenced - set(rule_names)):
        report.fail(f"README references missing file rules/{name}")


def main() -> int:
    print(f"Validating Flutter Cursor Rules plugin at {REPO_ROOT}")
    report = Reporter()
    validate_manifest(report)
    rule_names = validate_rules(report)
    validate_readme(report, rule_names)

    print("\n" + "-" * 60)
    if report.errors:
        print(f"RESULT: FAILED ({len(report.errors)} of {report.checks} checks failed)")
        for err in report.errors:
            print(f"  - {err}")
        return 1
    print(f"RESULT: OK ({report.checks} checks passed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
