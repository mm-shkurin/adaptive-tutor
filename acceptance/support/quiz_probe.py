from fastapi import Body, FastAPI, Request
from fastapi.responses import Response


def register_quiz_probe(app: FastAPI, quiz_tutor) -> None:
    from adapters.http.documents import _caller as document_caller

    @app.post("/acceptance/quiz-tutor/script", status_code=204)
    async def script_quiz_tutor(request: Request, body: dict = Body(...)):
        await document_caller(request)
        quiz_tutor.script(body["payload"])
        return Response(status_code=204)

    @app.post("/acceptance/quiz-tutor/fail", status_code=204)
    async def fail_quiz_tutor(request: Request):
        await document_caller(request)
        quiz_tutor.fail()
        return Response(status_code=204)
