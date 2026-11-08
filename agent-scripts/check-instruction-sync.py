from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLAUDE = ROOT / "CLAUDE.md"
COPILOT = ROOT / ".github" / "copilot-instructions.md"
MARKDOWN_LINK = re.compile(r"(!?\[[^\]]*\]\()([^)]+)(\))")


def normalized(text: str) -> str:
    def normalize_link(match: re.Match[str]) -> str:
        target = match.group(2)
        path_part, separator, fragment = target.partition("#")
        if path_part.startswith("../") and (COPILOT.parent / path_part).is_file():
            path_part = re.sub(r"^(?:\.\./)+", "", path_part)
        return f"{match.group(1)}{path_part}{separator}{fragment}{match.group(3)}"

    return MARKDOWN_LINK.sub(normalize_link, text)


def main() -> int:
    claude_text = CLAUDE.read_text(encoding="utf-8")
    copilot_text = normalized(COPILOT.read_text(encoding="utf-8"))
    if claude_text == copilot_text:
        print("CLAUDE.md and .github/copilot-instructions.md match after root-link normalization.")
        return 0

    print("Instruction files differ after root-link normalization:")
    diff = difflib.unified_diff(
        claude_text.splitlines(),
        copilot_text.splitlines(),
        fromfile="CLAUDE.md",
        tofile=".github/copilot-instructions.md (normalized)",
        lineterm="",
    )
    print("\n".join(diff))
    return 1


if __name__ == "__main__":
    sys.exit(main())
