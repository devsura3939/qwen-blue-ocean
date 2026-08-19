"""
FastAPI application main entry point.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config import settings
from database import init_db
from routers import countries, cities, categories, businesses, markets, jobs, exports


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting up Business Gap Finder API...")
    await init_db()
    print("Database initialized.")
    
    yield
    
    # Shutdown
    print("Shutting down Business Gap Finder API...")


app = FastAPI(
    title="Business Gap Finder API",
    description="Global local-business intelligence + competitive mapping + public contact discovery",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "error_code": "INTERNAL_ERROR"}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
    )


# Include routers
app.include_router(countries.router, prefix="/api/countries", tags=["Countries"])
app.include_router(cities.router, prefix="/api/cities", tags=["Cities"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(businesses.router, prefix="/api/businesses", tags=["Businesses"])
app.include_router(markets.router, prefix="/api/markets", tags=["Markets"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(exports.router, prefix="/api/exports", tags=["Exports"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
