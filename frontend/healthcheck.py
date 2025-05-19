"""
Health check endpoint for the Streamlit UI.
This file is imported by streamlit_app.py to add a health check endpoint.
"""
import streamlit as st
from streamlit.web.server.server import Server
import threading
import time
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks."""
    
    def do_GET(self):
        """Handle GET requests to the health check endpoint."""
        if self.path == "/healthz":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not Found")
    
    def log_message(self, format, *args):
        """Override to use our logger instead of stderr."""
        logger.debug("%s - - [%s] %s",
                     self.address_string(),
                     self.log_date_time_string(),
                     format % args)

def start_health_check_server(port=8501):
    """
    Start a simple HTTP server for health checks.
    
    Args:
        port: The port to listen on (default: 8501)
    """
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        logger.info(f"Starting health check server on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Error starting health check server: {e}")

def initialize_health_check():
    """Initialize the health check server in a background thread."""
    # Check if we're running in the Streamlit server
    if hasattr(st, "_is_running_with_streamlit") and st._is_running_with_streamlit:
        # Start the health check server in a daemon thread
        thread = threading.Thread(target=start_health_check_server, daemon=True)
        thread.start()
        logger.info("Health check endpoint initialized")
