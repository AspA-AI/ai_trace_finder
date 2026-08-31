import logging
from time import perf_counter

from fastapi import FastAPI, Request

from app.core.logging import configure_logging

from app.api.health import router as health_router
from app.api.investigations import router as investigations_router
from app.api.verification import router as verification_router
from app.api.reporting import router as reporting_router
from app.api.evaluation import router as evaluation_router

configure_logging()
log = logging.getLogger("trace.http")

app = FastAPI(title="People Investigation API", version="0.1.0")


@app.middleware("http")
async def request_logging(request: Request, call_next):
    started = perf_counter()
    log.info("request started method=%s path=%s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        log.exception(
            "request failed method=%s path=%s elapsed_ms=%.2f",
            request.method,
            request.url.path,
            (perf_counter() - started) * 1000,
        )
        raise
    log.info(
        "request completed method=%s path=%s status=%s elapsed_ms=%.2f",
        request.method,
        request.url.path,
        response.status_code,
        (perf_counter() - started) * 1000,
    )
    return response
app.include_router(health_router)
app.include_router(investigations_router)
app.include_router(verification_router)
app.include_router(reporting_router)
app.include_router(evaluation_router)
