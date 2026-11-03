import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.v1 import router as v1_router

app = FastAPI(
    title="BridgeIQ API",
    version="0.1.0",
    description="BridgeIQ: AI-Powered Hidden Talent Intelligence Box"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_timing_and_request_id(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Stage-Ms"] = str(duration_ms)
    return response


# Mount Routers
app.include_router(v1_router)


@app.get("/healthz", tags=["Ops"])
@app.get("/api/v1/healthz", tags=["Ops"])
def health_check():
    return {
        "status": "healthy",
        "service": "BridgeIQ API",
        "version": "0.1.0",
        "prompt_version": settings.prompt_version,
        "azure_openai_endpoint": settings.azure_openai_endpoint,
        "search_index_jobs": settings.search_index_jobs,
        "search_index_taxonomy": settings.search_index_taxonomy,
    }
