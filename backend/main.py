from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
import uvicorn
import os
from backend.api.routes import router
from backend.api.premium_features import router as premium_features_router
from backend.routes.analytics import router as analytics_router
from backend.routes.health_routes import router as health_router
from backend.routes import router as app_routes_router
from backend.auth.router import router as auth_router
from backend.services.monitoring.prometheusExporter import setup_prometheus_exporter, setup_fastapi_instrumentator
from backend.middleware.performanceMonitoring import PerformanceMonitoringMiddleware
from backend.services.monitoring.healthChecker import setup_health_checks

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

app = FastAPI(title="AI Content Humanizer")

def start_server():
    """Entry point for the API server when installed as a package."""
    import os
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8002"))  # Changed to 8002
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print(f"Starting Humanyze API on http://{host}:{port}")
    uvicorn.run("backend.main:app", host=host, port=port, log_level=log_level)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add performance monitoring middleware
app.add_middleware(PerformanceMonitoringMiddleware)

# Set up Prometheus exporter
setup_prometheus_exporter(app, endpoint="/api/metrics")
setup_fastapi_instrumentator(app)

# Set up health checks
setup_health_checks(app)

# API routes
app.include_router(router, prefix="/api")
app.include_router(premium_features_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(app_routes_router, prefix="/api")
app.include_router(auth_router, prefix="/api")

# Mount static files
app.mount("/static", StaticFiles(directory="backend/ui/static"), name="static")

# Serve the UI
@app.get("/")
async def serve_ui():
    return FileResponse("backend/ui/index.html")

@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup."""
    logger = logging.getLogger("startup")
    logger.info("Humanyze API started successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)  # Changed to 8002
