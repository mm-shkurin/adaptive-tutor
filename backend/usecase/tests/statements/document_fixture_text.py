from pathlib import Path

FIXTURES = Path(__file__).resolve().parents[4] / "acceptance" / "fixtures"
TABLE = "|Topic|Mark|\n|---|---|\n|Limits|91|\n"
TABLE_NAMED = "|Topic|Mark|\n|---|---|\n|Limits|91|"
FIVE_HUNDRED = (FIXTURES / "five_hundred.txt").read_text(encoding="utf-8")
JOINED = (FIXTURES / "joined.txt").read_text(encoding="utf-8")
EXTRACTED = (FIXTURES / "extracted.txt").read_text(encoding="utf-8")
NEIGHBOUR_TEXT = (FIXTURES / "neighbour.txt").read_text(encoding="utf-8")
