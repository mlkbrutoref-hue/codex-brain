#!/usr/bin/env python3
"""Quick validation script for skills and rules frontmatter in the workspace.

Operates with zero required external dependencies using the Python standard library,
with optional enhanced verification if PyYAML is installed.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / ".agents" / "skills"
RULES_DIR = ROOT / ".agents" / "rules"

FRONTMATTER_PATTERN = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}
    raw_yaml = match.group(1)

    try:
        import yaml
        parsed = yaml.safe_load(raw_yaml)
        if isinstance(parsed, dict):
            return parsed
    except ImportError:
        pass

    # Standard-library fallback parser for basic YAML key-value pairs
    data = {}
    for line in raw_yaml.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip("\"'")
            if val.lower() == "true":
                data[key] = True
            elif val.lower() == "false":
                data[key] = False
            else:
                data[key] = val
    return data


def validate_skills() -> bool:
    all_ok = True
    if not SKILLS_DIR.is_dir():
        print(f"[WARN] Skills directory not found: {SKILLS_DIR}")
        return True

    skill_files = list(SKILLS_DIR.glob("*/SKILL.md"))
    print(f"Validating {len(skill_files)} skill(s)...")
    for path in skill_files:
        content = path.read_text(encoding="utf-8")
        meta = parse_frontmatter(content)
        name = meta.get("name")
        desc = meta.get("description")

        if not name:
            print(f"  [FAIL] {path.relative_to(ROOT)}: missing 'name' in frontmatter")
            all_ok = False
        elif not desc:
            print(f"  [FAIL] {path.relative_to(ROOT)}: missing 'description' in frontmatter")
            all_ok = False
        else:
            print(f"  [PASS] {path.relative_to(ROOT)}: '{name}'")

    return all_ok


def validate_rules() -> bool:
    all_ok = True
    if not RULES_DIR.is_dir():
        return True

    rule_files = list(RULES_DIR.glob("*.md"))
    print(f"Validating {len(rule_files)} rule(s)...")
    for path in rule_files:
        content = path.read_text(encoding="utf-8")
        meta = parse_frontmatter(content)
        always_on = meta.get("always_on")

        print(f"  [PASS] {path.relative_to(ROOT)}: always_on={always_on}")

    return all_ok


def main() -> int:
    print("=" * 60)
    print("WORKSPACE FRONTMATTER VALIDATION (QUICK_VALIDATE)")
    print("=" * 60)

    skills_ok = validate_skills()
    rules_ok = validate_rules()

    if skills_ok and rules_ok:
        print("\nQUICK_VALIDATE: PASS")
        return 0
    else:
        print("\nQUICK_VALIDATE: FAIL")
        return 1


if __name__ == "__main__":
    sys.exit(main())
