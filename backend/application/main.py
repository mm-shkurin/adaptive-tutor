import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adapters.http.auth import router as auth_router
from adapters.http.chat import router as chat_router
from adapters.http.documents import router as documents_router
from adapters.http.errors import register_errors
from adapters.http.media import router as media_router
from adapters.http.profile import router as profile_router
from application.context import AppContext, build_production_context


def create_app(context: AppContext | None = None) -> FastAPI:
    ctx = context if context is not None else build_production_context()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        ctx._indexing = asyncio.Event()
        task = asyncio.create_task(_run_indexing(ctx))
        ctx._indexing.set()
        app.state.indexing_task = task
        yield
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

    app = FastAPI(title="AdaptiveTutor", lifespan=lifespan)
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
    app.include_router(documents_router, prefix="/api/v1/documents")
    app.include_router(chat_router, prefix="/api/v1/chat")
    return app


async def _run_indexing(ctx: AppContext) -> None:
    while True:
        await ctx.index_documents.index_waiting()
        if ctx._indexing is None:
            await asyncio.sleep(0.5)
            continue
        try:
            await asyncio.wait_for(ctx._indexing.wait(), timeout=0.5)
        except TimeoutError:
            continue
        ctx._indexing.clear()


def __getattr__(name: str):
    if name == "app":
        return create_app()
    raise AttributeError(name)
