"""Inject or snapshot AdaptiveTutor session context. Fail open."""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BANK = ROOT / ".memory-bank" / "index.md"
STORIES = ROOT / "ProductSpecification" / "stories.md"
STORY_ROOT = ROOT / "ProductSpecification" / "stories"
LOG = ROOT / ".memory-bank" / "session-log.md"


def digest() -> str:
    parts = [
        "AdaptiveTutor session context. Read these before asking the user to restate the plan.",
        f"Encyclopedia: {BANK.relative_to(ROOT).as_posix()}",
        f"Story rollup: {STORIES.relative_to(ROOT).as_posix()}",
    ]
    if BANK.exists():
        text = BANK.read_text(encoding="utf-8")
        parts.append("Memory bank index:\n" + text[:1800])
    current = []
    if STORY_ROOT.exists():
        for progress in sorted(STORY_ROOT.glob("*/progress.md")):
            for line in progress.read_text(encoding="utf-8").splitlines():
                if "[~]" in line or "[ ]" in line:
                    current.append(f"{progress.parent.name}: {line.strip()}")
                    if "[~]" in line:
                        break
            if len(current) >= 8:
                break
    if current:
        parts.append("Next progress lines:\n" + "\n".join(current))
    parts.append(
        "Do not write API or test specs for a story until its interview is confirmed. "
        "Story 1 interview exists; its next step is the story spec."
    )
    return "\n\n".join(parts)


def emit(payload: dict) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdout.write(json.dumps(payload, ensure_ascii=True))


def main() -> int:
    event = sys.argv[1] if len(sys.argv) > 1 else "sessionStart"
    try:
        sys.stdin.read()
    except Exception:
        pass
    try:
        if event == "sessionEnd":
            LOG.parent.mkdir(parents=True, exist_ok=True)
            with LOG.open("a", encoding="utf-8") as handle:
                handle.write(f"- {datetime.now().isoformat(timespec='minutes')} session end\n")
            emit({})
            return 0
        text = digest()
        if event == "preCompact":
            emit({"additional_context": text})
        else:
            emit({"additional_context": text})
    except Exception:
        emit({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
