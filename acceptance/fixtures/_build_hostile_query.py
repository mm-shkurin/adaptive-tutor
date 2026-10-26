import pymupdf
from pathlib import Path

MIN = 1_048_576
text = "' OR 1=1 in pdf body"
doc = pymupdf.open()
page = doc.new_page()
page.insert_text((72, 72), text, fontsize=12)
raw = doc.tobytes()
doc.close()
if len(raw) < MIN:
    raw = raw + b"\n%" + b"0" * (MIN - len(raw) - 1)
path = Path(__file__).resolve().parent / "hostile_query.pdf"
path.write_bytes(raw)
print(len(raw))
