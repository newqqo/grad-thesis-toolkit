from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "agents/README.md",
    "agents/shared/thesis-agent-core.md",
    "agents/shared/command-map.md",
    "agents/codex/skills/grad-thesis-agent/SKILL.md",
    ".agents/skills/grad-thesis-agent/SKILL.md",
    ".claude/commands/thesis/concept-tree.md",
    ".claude/commands/thesis/promise-delivery.md",
    ".claude/commands/thesis/literature-map.md",
    ".claude/commands/thesis/outline-intake.md",
    ".claude/agents/thesis-reviewer.md",
    ".gemini/commands/thesis/concept-tree.toml",
    ".gemini/commands/thesis/promise-delivery.toml",
    ".gemini/commands/thesis/literature-map.toml",
    ".gemini/commands/thesis/outline-intake.toml",
]

REQUIRED_SHARED_TERMS = [
    "concept hierarchy",
    "Promise-Delivery",
    "citation",
    "literature",
    "privacy",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def has_frontmatter(text: str) -> bool:
    return bool(re.match(r"^---\n.+?\n---\n", text, flags=re.DOTALL))


def check_required_files() -> list[str]:
    problems = []
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.exists():
            problems.append(f"missing required adapter file: {relative}")
    return problems


def check_skill_frontmatter() -> list[str]:
    problems = []
    for relative in [
        "agents/codex/skills/grad-thesis-agent/SKILL.md",
        ".agents/skills/grad-thesis-agent/SKILL.md",
    ]:
        text = read(ROOT / relative)
        if not has_frontmatter(text):
            problems.append(f"skill missing YAML frontmatter: {relative}")
        if "description:" not in text:
            problems.append(f"skill missing description field: {relative}")
    return problems


def check_toml_commands() -> list[str]:
    problems = []
    for path in (ROOT / ".gemini" / "commands" / "thesis").glob("*.toml"):
        try:
            data = tomllib.loads(read(path))
        except tomllib.TOMLDecodeError as exc:
            problems.append(f"invalid TOML: {path.relative_to(ROOT)}: {exc}")
            continue
        if not data.get("description"):
            problems.append(f"missing description in {path.relative_to(ROOT)}")
        if not data.get("prompt"):
            problems.append(f"missing prompt in {path.relative_to(ROOT)}")
    return problems


def check_shared_core() -> list[str]:
    text = read(ROOT / "agents" / "shared" / "thesis-agent-core.md").lower()
    return [f"shared core missing term: {term}" for term in REQUIRED_SHARED_TERMS if term.lower() not in text]


def main() -> int:
    problems = []
    problems.extend(check_required_files())
    if not problems:
        problems.extend(check_skill_frontmatter())
        problems.extend(check_toml_commands())
        problems.extend(check_shared_core())
    if problems:
        print("Agent adapter check failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("Agent adapter check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
