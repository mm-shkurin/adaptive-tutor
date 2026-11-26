import time
from uuid import UUID

from tests.presentation_flow import add_image, create, index, token
from tests.support import build


def test_forty_slide_index_finishes_within_five_minutes():
    bundle = build()
    access = token(bundle)
    presentation_id = create(bundle, access).json()["id"]
    for slide_index in range(40):
        added = add_image(bundle, access, presentation_id, key=f"load-{slide_index}")
        assert added.status_code == 200
        slide_id = added.json()["slides"][slide_index]["id"]
        bundle.ocr.set_text(UUID(slide_id), f"slide {slide_index}")
    started = time.monotonic()
    indexed = index(bundle, access, presentation_id)
    elapsed = time.monotonic() - started
    assert indexed.status_code == 202
    body = indexed.json()
    assert body["status"] in {"ready", "failed"}
    assert body["status"] != "indexing"
    assert elapsed < 300
