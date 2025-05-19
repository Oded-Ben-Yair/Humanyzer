"""
Health check utilities for the API.
"""
from fastapi import FastAPI, Depends, HTTPException, status
import time
import os
import psutil
import platform

def setup_health_checks(app: FastAPI):
    """
    Set up health check endpoints.
    
    Args:
        app: FastAPI application
    """
    @app.get("/health")
    async def health_check():
        """Basic health check endpoint."""
        return {
            "status": "ok",
            "timestamp": time.time()
        }
    
    @app.get("/health/detailed")
    async def detailed_health_check():
        """Detailed health check endpoint."""
        # Get system info
        system_info = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }
        
        # Check if system resources are within acceptable limits
        status_ok = (
            system_info["cpu_percent"] < 90 and
            system_info["memory_percent"] < 90 and
            system_info["disk_percent"] < 90
        )
        
        return {
            "status": "ok" if status_ok else "warning",
            "timestamp": time.time(),
            "system_info": system_info
        }
