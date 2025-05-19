
"""
Utility for recording application metrics.
"""
from prometheus_client import Counter, Gauge, Histogram, Summary
import time
from typing import Dict, Any, Optional, Callable

# Define common metrics
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 30.0, 60.0)
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active', 
    'Number of active HTTP requests',
    ['method', 'endpoint']
)

ERROR_COUNT = Counter(
    'http_request_errors_total', 
    'Total number of HTTP request errors',
    ['method', 'endpoint', 'error_type']
)

# Database metrics
DB_QUERY_LATENCY = Histogram(
    'db_query_duration_seconds', 
    'Database query latency in seconds',
    ['query_type', 'table'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)

DB_CONNECTION_POOL = Gauge(
    'db_connection_pool_size', 
    'Database connection pool size',
    ['pool_name']
)

# Business metrics
USER_SIGNUPS = Counter(
    'user_signups_total', 
    'Total number of user signups',
    ['source']
)

FEATURE_USAGE = Counter(
    'feature_usage_total', 
    'Total number of feature usages',
    ['feature_name', 'subscription_tier']
)

API_RATE_LIMIT_EXCEEDED = Counter(
    'api_rate_limit_exceeded_total', 
    'Total number of API rate limit exceeded events',
    ['endpoint', 'user_id']
)

# System metrics
MEMORY_USAGE = Gauge(
    'memory_usage_bytes', 
    'Memory usage in bytes'
)

CPU_USAGE = Gauge(
    'cpu_usage_percent', 
    'CPU usage percentage'
)

# Helper functions
def track_request_latency(method: str, endpoint: str) -> Callable:
    """
    Decorator to track request latency.
    
    Args:
        method: HTTP method
        endpoint: API endpoint
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).inc()
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                ERROR_COUNT.labels(
                    method=method, 
                    endpoint=endpoint, 
                    error_type=type(e).__name__
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
                ACTIVE_REQUESTS.labels(method=method, endpoint=endpoint).dec()
        return wrapper
    return decorator

def track_db_query_latency(query_type: str, table: str) -> Callable:
    """
    Decorator to track database query latency.
    
    Args:
        query_type: Type of query (SELECT, INSERT, UPDATE, DELETE)
        table: Database table name
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                DB_QUERY_LATENCY.labels(query_type=query_type, table=table).observe(duration)
        return wrapper
    return decorator

def record_feature_usage(feature_name: str, subscription_tier: str) -> None:
    """
    Record feature usage.
    
    Args:
        feature_name: Name of the feature
        subscription_tier: Subscription tier of the user
    """
    FEATURE_USAGE.labels(feature_name=feature_name, subscription_tier=subscription_tier).inc()

def update_system_metrics(memory_bytes: float, cpu_percent: float) -> None:
    """
    Update system metrics.
    
    Args:
        memory_bytes: Memory usage in bytes
        cpu_percent: CPU usage percentage
    """
    MEMORY_USAGE.set(memory_bytes)
    CPU_USAGE.set(cpu_percent)
