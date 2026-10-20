from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adapters.http.auth import router as auth_router
from adapters.http.errors import register_errors
from adapters.http.media import router as media_router
from adapters.http.profile import router as profile_router
from application.context import AppContext, build_production_context


def create_app(context: AppContext | None = None) -> FastAPI:
    ctx = context if context is not None else build_production_context()
    app = FastAPI(title="AdaptiveTutor")
    app.state.ctx = ctx
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(ctx.config.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_errors(app)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.include_router(auth_router, prefix="/api/v1/auth")
    app.include_router(profile_router, prefix="/api/v1/user")
    app.include_router(media_router, prefix="/api/v1/media")
    return app


def __getattr__(name: str):
    if name == "app":
        return create_app()
    raise AttributeError(name)
