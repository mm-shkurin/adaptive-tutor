_THIN_CHARS = 40
_MIN_BYTES_FOR_THIN = 10_000


def is_weak_ocr(text: str, size_bytes: int) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if size_bytes >= _MIN_BYTES_FOR_THIN and len(stripped) < _THIN_CHARS:
        return True
    return _looks_broken_formula(stripped)


def _looks_broken_formula(text: str) -> bool:
    if len(text) > 120:
        return False
    odd = sum(1 for char in text if char in "¯¨¸°′″∫∑∏√∞≈≠≤≥±×÷")
    letters = sum(1 for char in text if char.isalpha())
    return odd >= 2 and letters <= odd
