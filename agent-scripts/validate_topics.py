from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
START = ROOT / "start.md"
TRACKER = ROOT / "progress.html"
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
TRACKER_TOPIC_PATTERN = re.compile(
    r"\{id:'(\d+)',priority:'([^']+)',name:'([^']+)'"
    r"(?:,notes:'([^']+)',exercises:'([^']+)')?\}"
)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_index() -> list[dict[str, str]]:
    topics = []
    for line in START.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\|\s*\d{2}\s*\|", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            continue
        note_match = LINK_PATTERN.search(cells[3])
        exercise_match = LINK_PATTERN.search(cells[4])
        topics.append(
            {
                "id": cells[0],
                "title": cells[1],
                "slug": cells[2],
                "notes": note_match.group(1) if note_match else "",
                "exercises": exercise_match.group(1) if exercise_match else "",
            }
        )
    return topics


def check_local_links(path: Path, text: str, errors: list[str]) -> None:
    for target in LINK_PATTERN.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        local_target = target.split("#", 1)[0]
        if not local_target:
            continue
        resolved = (path.parent / local_target).resolve()
        if not resolved.is_file():
            fail(errors, f"{path.relative_to(ROOT)}: missing link target {target}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    topics = parse_index()
    if len(topics) != 24:
        fail(errors, f"start.md: expected 24 topic rows, found {len(topics)}")

    tracker_text = TRACKER.read_text(encoding="utf-8")
    tracker_topics = TRACKER_TOPIC_PATTERN.findall(tracker_text)
    expected_ids = [topic["id"] for topic in topics]
    actual_ids = [topic[0] for topic in tracker_topics]
    if actual_ids != expected_ids:
        fail(errors, "progress.html: topic IDs/order do not match start.md")

    for topic, tracker_topic in zip(topics, tracker_topics):
        topic_id, priority, title, tracker_notes, tracker_exercises = tracker_topic
        if title != topic["title"]:
            fail(errors, f"progress.html: title mismatch for topic {topic_id}")
        for column in ("notes", "exercises"):
            suffix = "-exercises" if column == "exercises" else ""
            expected_path = f"notes/{topic['id']}-{topic['slug']}{suffix}.md"
            if topic[column] != expected_path:
                fail(errors, f"start.md: topic {topic['id']} has missing or incorrect {column} link")
            if not (ROOT / expected_path).is_file():
                fail(errors, f"topic {topic['id']}: missing file {expected_path}")
        if tracker_notes != topic["notes"] or tracker_exercises != topic["exercises"]:
            fail(errors, f"progress.html: links mismatch for topic {topic_id}")
        if priority not in {"Core", "Useful", "Optional"}:
            fail(errors, f"progress.html: invalid priority for topic {topic_id}")

        note_path = ROOT / topic["notes"]
        exercise_path = ROOT / topic["exercises"]
        if not note_path.is_file() or not exercise_path.is_file():
            continue
        note_text = note_path.read_text(encoding="utf-8")
        exercise_text = exercise_path.read_text(encoding="utf-8")

        if Path(topic["exercises"]).name not in note_text:
            fail(errors, f"{note_path.relative_to(ROOT)}: missing exercise link")
        if "../start.md" not in note_text:
            fail(errors, f"{note_path.relative_to(ROOT)}: missing topic-index link")
        if Path(topic["notes"]).name not in exercise_text:
            fail(errors, f"{exercise_path.relative_to(ROOT)}: missing note link")
        if "../start.md" not in exercise_text:
            fail(errors, f"{exercise_path.relative_to(ROOT)}: missing topic-index link")
        check_local_links(note_path, note_text, errors)
        check_local_links(exercise_path, exercise_text, errors)

        questions = re.findall(r"(?m)^## (\d+)\. ", exercise_text)
        expected_results = re.findall(r"(?m)^\*\*Expected result:\*\*", exercise_text)
        answers = re.findall(r"<details>", exercise_text)
        summaries = re.findall(r"<summary>Show answer</summary>", exercise_text)
        if questions != [str(number) for number in range(1, 13)]:
            fail(errors, f"{exercise_path.relative_to(ROOT)}: expected questions numbered 1-12")
        if len(expected_results) != 12:
            fail(errors, f"{exercise_path.relative_to(ROOT)}: expected 12 Expected result paragraphs")
        if len(answers) != 12 or len(summaries) != 12 or exercise_text.count("</details>") != 12:
            fail(errors, f"{exercise_path.relative_to(ROOT)}: expected 12 complete answer disclosures")

        prose = re.sub(r"```.*?```", " ", note_text, flags=re.DOTALL)
        words = len(re.findall(r"\b[\w'-]+\b", prose))
        if not 300 <= words <= 600:
            warnings.append(f"{note_path.relative_to(ROOT)}: {words} prose words (target 300-600)")

    if errors:
        print("Topic validation failed:")
        for error in errors:
            print(f"- {error}")
    else:
        print(f"Validated {len(topics)} topic pairs, index links, tracker links, and exercise structure.")
    if warnings:
        print("Note-length warnings:")
        for warning in warnings:
            print(f"- {warning}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
