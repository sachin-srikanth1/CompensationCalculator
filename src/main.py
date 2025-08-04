from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .api.compare import router as compare_router
from .api.scenario import router as scenario_router
from .api.benchmarks import router as benchmarks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Compensation Comparison Tool API...")
    yield
    # Shutdown
    print("👋 Shutting down Compensation Comparison Tool API...")


# Create FastAPI app
app = FastAPI(
    title="Compensation Comparison Tool API",
    description="A comprehensive API for comparing compensation offers and running what-if scenarios",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(compare_router)
app.include_router(scenario_router)
app.include_router(benchmarks_router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Compensation Comparison Tool API",
        "version": "1.0.0",
        "endpoints": {
            "compare": "/compare",
            "scenarios": "/scenario",
            "benchmarks": "/benchmarks",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "compensation-comparison-tool",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 