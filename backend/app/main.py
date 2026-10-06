from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import DomainError, domain_error_handler, validation_error_handler
from app.scripts.seed import seed

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Guarantee that the self-contained demo account exists after every deploy."""
    seed()
    yield


app = FastAPI(
    title="Route 53 Console Clone API",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/docs",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.include_router(api_router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["Health"])
def health():
    return {"status": "ok"}
