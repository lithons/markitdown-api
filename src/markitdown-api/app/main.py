# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware import Middleware
from starlette.middleware.gzip import GZipMiddleware
import logging

from app.api.converter import router as converter_router
from app.core.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

middleware = [
    Middleware(GZipMiddleware, minimum_size=1024),
]

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESC,
    version=settings.APP_VERSION,
    docs_url=None,
    redoc_url=None,
    middleware=middleware,
)

# CORS (optional)
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if settings.ENV == "production" and settings.PUBLIC_BASE_URL:
    host = settings.PUBLIC_BASE_URL.host
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[host, f".{host}"])

# Routes
app.include_router(converter_router)

@app.get("/scalar", include_in_schema=False)
async def scalar_html(request: Request):
    server_url = str(settings.PUBLIC_BASE_URL or request.base_url).rstrip("/")
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
        servers=[{"url": server_url, "description": f"{settings.ENV.capitalize()} server"}],
    )

# Meta & health
@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} is running.", "env": settings.ENV}

@app.get("/temp")
async def temp():
    return {"message": f"{settings.APP_NAME} is running.", "env": settings.ENV}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}


# Dev-only entrypoint. In prod, launch via CLI (see below).
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
