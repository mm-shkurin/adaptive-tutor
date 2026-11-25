from usecase.presentation.add_slides import AddSlides
from usecase.presentation.create_presentation import CreatePresentation
from usecase.presentation.delete_presentation import DeletePresentation
from usecase.presentation.get_presentation import GetPresentation
from usecase.presentation.get_progress import GetProgress
from usecase.presentation.index_presentation import IndexPresentation
from usecase.presentation.patch_presentation import PatchPresentation


def wire_presentations(documents, pieces, presentations, ocr, virus, clock) -> dict:
    return {
        "create_presentation": CreatePresentation(presentations, documents, clock),
        "get_presentation": GetPresentation(presentations),
        "patch_presentation": PatchPresentation(presentations, documents),
        "delete_presentation": DeletePresentation(presentations, documents, pieces),
        "add_slides": AddSlides(presentations, documents, virus),
        "index_presentation": IndexPresentation(presentations, documents, pieces, ocr),
        "get_progress": GetProgress(),
    }