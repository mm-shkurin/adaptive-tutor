from fastapi import APIRouter

router = APIRouter()


@router.post("/messages", status_code=202)
async def accept_message():
    return {"status": "accepted"}
