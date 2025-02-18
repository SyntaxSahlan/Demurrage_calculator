import os
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from loguru import logger
from prometheus_client import Counter, Histogram
from starlette_exporter import PrometheusMiddleware, handle_metrics
from models import ContainerType, ContainerSize, DemurrageRequest, DemurrageResponse, ChargeBreakdown
from demurrage_calculator import calculate_demurrage

# Configure logging
logger.add("api.log", rotation="500 MB", level="INFO")

# Initialize metrics
REQUESTS = Counter('http_requests_total', 'Total HTTP requests')
REQUESTS_TIME = Histogram('request_processing_seconds', 'Time spent processing request')
DEMURRAGE_CALC = Counter('demurrage_calculations_total', 'Total demurrage calculations')

app = FastAPI(title="Demurrage Calculator API")

# Add Prometheus middleware
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

# Custom timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request processed in {process_time:.4f} seconds")
    REQUESTS_TIME.observe(process_time)
    return response

@app.get("/health")
async def health_check():
    return {"status": "ok"}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve index.html at root path
@app.get("/")
async def read_root():
    return FileResponse('index.html')

# Mount static files directory if it exists
if os.path.exists('static'):
    app.mount("/static", StaticFiles(directory="static"), name="static")
@app.post("/calculate-demurrage", response_model=DemurrageResponse)
@cache(
    expire=3600,
    key_builder=lambda demurrage_request, **kwargs: f"demurrage:{demurrage_request.container_type}:{demurrage_request.container_size}:{demurrage_request.days}"
)
async def calculate_demurrage_charge(demurrage_request: DemurrageRequest):
    try:
        logger.info(f"Processing demurrage calculation for {demurrage_request.container_type} {demurrage_request.container_size} for {demurrage_request.days} days")
        DEMURRAGE_CALC.inc()
        
        total_charge, breakdown_dict = calculate_demurrage(
            demurrage_request.container_type,
            demurrage_request.container_size,
            demurrage_request.days
        )

        breakdown = [
            ChargeBreakdown(
                period_name=period_name,
                days=details['days'],
                rate=details['rate'],
                charge=details['charge']
            )
            for period_name, details in breakdown_dict.items()
        ]

        return DemurrageResponse(
            total_charge=total_charge,
            breakdown=breakdown
        )
    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating demurrage: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.on_event("startup")
async def startup():
    # Initialize FastAPI cache with Redis backend
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    logger.info("Application started, cache initialized")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8006))
    workers = int(os.environ.get("WORKERS", 4))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        workers=workers,
        log_level="info"
    )
