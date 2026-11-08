# Agent Scripts

Run these scripts from the repository root with Python 3.10+; they use only the standard library and do not modify files.

- `python agent-scripts/validate_topics.py` replaces one-off PowerShell checks of exercise files. It checks all 24 topic rows, note/exercise paths and reciprocal links, tracker IDs/order/titles/links, exactly 12 numbered questions, 12 `Expected result` paragraphs, 12 complete answer disclosures per exercise, local Markdown links, and note-length targets. Missing files, broken links, or invalid exercise structure return exit code 1. Note word-count differences are reported as warnings.
- `python agent-scripts/check-instruction-sync.py` compares `CLAUDE.md` with `.github/copilot-instructions.md` after removing leading `../` from Copilot root-relative Markdown links. It prints a unified diff and returns exit code 1 when substantive differences remain.

These checks validate structure and synchronization, not SQL execution or the factual correctness of every answer. Run SQL fixtures only in an authorized isolated practice schema.
