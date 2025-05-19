
"""
Error reporting utility for the application.
"""
import logging
import traceback
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

def initialize_error_reporting(dsn: Optional[str] = None) -> None:
    """
    Initialize error reporting with Sentry.
    
    Args:
        dsn: Sentry DSN (Data Source Name)
    """
    if not dsn:
        dsn = os.getenv("SENTRY_DSN")
    
    if not dsn:
        logger.warning("Sentry DSN not provided. Error reporting will not be enabled.")
        return
    
    environment = os.getenv("ENVIRONMENT", "development")
    
    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
        ],
        environment=environment,
        traces_sample_rate=0.2,  # Adjust based on traffic volume
        send_default_pii=False,  # Avoid sending personally identifiable information
    )
    
    logger.info(f"Sentry initialized for environment: {environment}")

def capture_exception(
    exception: Exception, 
    context: Optional[Dict[str, Any]] = None,
    level: str = "error"
) -> str:
    """
    Capture and report an exception to Sentry.
    
    Args:
        exception: The exception to report
        context: Additional context data
        level: Error level (error, warning, info)
        
    Returns:
        Event ID of the captured exception
    """
    if not context:
        context = {}
    
    # Log the exception locally
    logger.error(
        f"Exception: {str(exception)}\nTraceback: {traceback.format_exc()}\nContext: {context}"
    )
    
    # Report to Sentry if available
    try:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            
            scope.level = level
            return sentry_sdk.capture_exception(exception)
    except Exception as e:
        logger.error(f"Failed to report to Sentry: {str(e)}")
        return "error-reporting-failed"

def capture_message(
    message: str, 
    context: Optional[Dict[str, Any]] = None,
    level: str = "info"
) -> str:
    """
    Capture and report a message to Sentry.
    
    Args:
        message: The message to report
        context: Additional context data
        level: Error level (error, warning, info)
        
    Returns:
        Event ID of the captured message
    """
    if not context:
        context = {}
    
    # Log the message locally
    log_method = getattr(logger, level, logger.info)
    log_method(f"Message: {message}\nContext: {context}")
    
    # Report to Sentry if available
    try:
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            
            scope.level = level
            return sentry_sdk.capture_message(message)
    except Exception as e:
        logger.error(f"Failed to report message to Sentry: {str(e)}")
        return "error-reporting-failed"

def set_user_context(user_id: str, email: Optional[str] = None) -> None:
    """
    Set user context for error reporting.
    
    Args:
        user_id: User ID
        email: User email
    """
    try:
        sentry_sdk.set_user({"id": user_id, "email": email})
    except Exception as e:
        logger.error(f"Failed to set user context in Sentry: {str(e)}")
