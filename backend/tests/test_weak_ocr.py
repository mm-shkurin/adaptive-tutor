from domain.presentation.weak_ocr import is_weak_ocr


def test_thin_ocr_on_large_image_is_weak():
    assert is_weak_ocr("ab", 20_000) is True


def test_rich_ocr_is_not_weak():
    assert is_weak_ocr("A full sentence of lecture text about matrices.", 20_000) is False


def test_empty_ocr_is_not_weak():
    assert is_weak_ocr("   ", 50_000) is False


def test_broken_formula_glyphs_are_weak():
    assert is_weak_ocr("∑ ∫ ≈", 100) is True
