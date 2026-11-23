from fastapi import Body, FastAPI, Request
from fastapi.responses import Response

from support.tutor_hold import TutorHold


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

    @app.post("/acceptance/quiz-tutor/hold", status_code=204)
    async def hold_quiz_tutor(request: Request):
        await document_caller(request)
        hold = TutorHold()
        quiz_tutor.hold(hold._entered, hold._release)
        quiz_tutor._hold = hold
        return Response(status_code=204)

    @app.post("/acceptance/quiz-tutor/release", status_code=204)
    async def release_quiz_tutor(request: Request):
        await document_caller(request)
        hold = getattr(quiz_tutor, "_hold", None)
        if hold is not None:
            hold.release()
        return Response(status_code=204)

    @app.get("/acceptance/quiz-tutor/holds")
    async def quiz_tutor_holds(request: Request):
        await document_caller(request)
        entered = quiz_tutor._entered is not None and quiz_tutor._entered.is_set()
        return {"entered": 1 if entered else 0}
