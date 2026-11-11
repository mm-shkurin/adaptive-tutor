from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/messages", status_code=202)
async def accept_message(request: Request):
    hold = getattr(request.app.state, "peak_chat_hold", None)
    if hold is not None:
        await hold.enter()
    return {"status": "accepted"}
