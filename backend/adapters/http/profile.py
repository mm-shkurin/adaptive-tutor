from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field

from adapters.http.auth import _bearer
from adapters.http.uploads import read_upload
from domain.account.name import NAME_LIMIT

router = APIRouter()


class ProfileNameBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(max_length=NAME_LIMIT)


@router.get("/profile")
async def read_profile(request: Request):
    ctx = request.app.state.ctx
    account = await ctx.session.caller(_bearer(request))
    return ctx.profile.view(account)


@router.patch("/profile")
async def rename_profile(body: ProfileNameBody, request: Request):
    ctx = request.app.state.ctx
    account = await ctx.session.caller(_bearer(request))
    return await ctx.profile.rename(account, body.name)


@router.put("/avatar")
async def upload_avatar(request: Request, file: UploadFile = File(...)):
    ctx = request.app.state.ctx
    account = await ctx.session.caller(_bearer(request))
    return await ctx.profile.replace_photo(account, await read_upload(file))


@router.delete("/avatar")
async def remove_avatar(request: Request):
    ctx = request.app.state.ctx
    account = await ctx.session.caller(_bearer(request))
    return await ctx.profile.remove_photo(account)


@router.delete("", status_code=204)
async def delete_account(request: Request):
    ctx = request.app.state.ctx
    account = await ctx.session.caller(_bearer(request))
    await ctx.profile.remove_account(account)
    return Response(status_code=204)
