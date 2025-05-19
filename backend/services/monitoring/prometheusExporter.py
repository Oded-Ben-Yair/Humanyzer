"""
Prometheus metrics exporter for the API.
"""
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
import time

# Define metrics
REQUEST_COUNT = Counter(
    "humanyze_request_count",
    "Number of requests received",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "humanyze_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"]
)

def setup_prometheus_exporter(app: FastAPI, endpoint: str = "/metrics"):
    """
    Set up Prometheus metrics endpoint.
    
    Args:
        app: FastAPI application
        endpoint: Metrics endpoint
    """
    @app.get(endpoint)
    async def metrics():
        """Prometheus metrics endpoint."""
        return Response(
            generate_latest(REGISTRY),
            media_type=CONTENT_TYPE_LATEST
        )

def setup_fastapi_instrumentator(app: FastAPI):
    """
    Set up FastAPI instrumentator for Prometheus metrics.
    
    Args:
        app: FastAPI application
    """
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app)
