from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel, ConfigDict

BROWSER_COOKIE = "signin_browser"

router = APIRouter()


class ExchangeBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    code: str


class RefreshBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    refresh_token: str


@router.get("/oauth/yandex/start")
async def start_yandex(request: Request):
    ctx = request.app.state.ctx
    url, browser = await ctx.sign_in.start()
    response = RedirectResponse(url, status_code=302)
    response.set_cookie(
        key=BROWSER_COOKIE,
        value=browser,
        max_age=int(ctx.config.state_ttl.total_seconds()),
        httponly=True,
        samesite="lax",
        path="/",
    )
    return response


@router.get("/oauth/yandex/callback")
async def finish_yandex(request: Request, code: str = "", state: str = "", error: str = ""):
    location = await request.app.state.ctx.sign_in.callback(code, state, error)
    return RedirectResponse(location, status_code=302)


@router.post("/oauth/exchange")
async def exchange(body: ExchangeBody, request: Request):
    pair = await request.app.state.ctx.sign_in.exchange(body.code, request.cookies.get(BROWSER_COOKIE, ""))
    return {"access_token": pair.access_token, "refresh_token": pair.refresh_token, "token_type": pair.token_type}


@router.post("/refresh")
async def refresh(body: RefreshBody, request: Request):
    pair = await request.app.state.ctx.session.refresh(body.refresh_token)
    return {"access_token": pair.access_token, "refresh_token": pair.refresh_token, "token_type": pair.token_type}


@router.post("/logout", status_code=204)
async def logout(request: Request):
    refresh_token = await _refresh_token(request)
    await request.app.state.ctx.session.logout(_bearer(request), refresh_token)
    return Response(status_code=204)


def _bearer(request: Request) -> str | None:
    header = request.headers.get("authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header[7:].strip()
    return token or None


async def _refresh_token(request: Request) -> str | None:
    if not request.headers.get("content-type", "").startswith("application/json"):
        return None
    payload = await request.json()
    if not isinstance(payload, dict):
        return None
    refresh_token = payload.get("refresh_token")
    if refresh_token is None:
        return None
    if not isinstance(refresh_token, str):
        return None
    return refresh_token
