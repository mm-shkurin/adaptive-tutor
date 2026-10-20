from usecase.document.ports import DocumentIntake, FileStore, PdfReader, PieceIndex


class IndexDocuments:
    def __init__(self, intake: DocumentIntake, files: FileStore, reader: PdfReader, pieces: PieceIndex):
        self.intake = intake
        self.files = files
        self.reader = reader
        self.pieces = pieces

    async def index_waiting(self) -> None:
        raise NotImplementedError()
