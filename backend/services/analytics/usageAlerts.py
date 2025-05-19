
"""
Usage alerts service for API analytics.

This module provides functionality to monitor API usage and
send alerts when thresholds are exceeded.
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time

from app.services.analytics.usageTracker import usage_tracker
from app.config import settings

# Configure logger
logger = logging.getLogger("usage_alerts")

class UsageAlerts:
    """
    Service for monitoring API usage and sending alerts.
    
    This class provides methods to define usage thresholds and
    send notifications when those thresholds are exceeded.
    """
    
    def __init__(self):
        """Initialize the usage alerts service."""
        self.enabled = getattr(settings, "ENABLE_USAGE_ALERTS", True)
        self.check_interval = getattr(settings, "USAGE_ALERT_CHECK_INTERVAL", 3600)  # 1 hour
        self.thresholds = {}
        
        # Load default thresholds
        self._load_default_thresholds()
    
    def _load_default_thresholds(self):
        """Load default usage thresholds."""
        self.thresholds = {
            "daily": {
                "warning": 10000,  # 10,000 requests per day
                "critical": 20000  # 20,000 requests per day
            },
            "monthly": {
                "warning": 250000,  # 250,000 requests per month
                "critical": 500000  # 500,000 requests per month
            }
        }
    
    def set_threshold(self, customer_id: str, period: str, level: str, value: int):
        """
        Set a usage threshold for a customer.
        
        Args:
            customer_id: Customer identifier
            period: Time period (daily, monthly)
            level: Alert level (warning, critical)
            value: Threshold value
        """
        if customer_id not in self.thresholds:
            self.thresholds[customer_id] = {
                "daily": {
                    "warning": self.thresholds["daily"]["warning"],
                    "critical": self.thresholds["daily"]["critical"]
                },
                "monthly": {
                    "warning": self.thresholds["monthly"]["warning"],
                    "critical": self.thresholds["monthly"]["critical"]
                }
            }
        
        self.thresholds[customer_id][period][level] = value
        logger.info(f"Set {level} threshold for {customer_id} {period} usage to {value}")
    
    async def check_thresholds(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Check if any thresholds have been exceeded.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            List of triggered alerts
        """
        if not self.enabled:
            return []
        
        alerts = []
        now = datetime.now()
        
        # Get customer-specific thresholds or use defaults
        customer_thresholds = self.thresholds.get(customer_id, self.thresholds)
        
        # Check daily thresholds
        daily_stats = await usage_tracker.get_usage_stats(
            customer_id=customer_id,
            start_time=datetime(now.year, now.month, now.day),
            end_time=now,
            bucket_type="hour"
        )
        
        daily_usage = daily_stats.get("total_requests", 0)
        daily_warning = customer_thresholds["daily"]["warning"]
        daily_critical = customer_thresholds["daily"]["critical"]
        
        if daily_usage >= daily_critical:
            alerts.append({
                "customer_id": customer_id,
                "period": "daily",
                "level": "critical",
                "threshold": daily_critical,
                "current_usage": daily_usage,
                "timestamp": int(time.time())
            })
        elif daily_usage >= daily_warning:
            alerts.append({
                "customer_id": customer_id,
                "period": "daily",
                "level": "warning",
                "threshold": daily_warning,
                "current_usage": daily_usage,
                "timestamp": int(time.time())
            })
        
        # Check monthly thresholds
        monthly_stats = await usage_tracker.get_usage_stats(
            customer_id=customer_id,
            start_time=datetime(now.year, now.month, 1),
            end_time=now,
            bucket_type="day"
        )
        
        monthly_usage = monthly_stats.get("total_requests", 0)
        monthly_warning = customer_thresholds["monthly"]["warning"]
        monthly_critical = customer_thresholds["monthly"]["critical"]
        
        if monthly_usage >= monthly_critical:
            alerts.append({
                "customer_id": customer_id,
                "period": "monthly",
                "level": "critical",
                "threshold": monthly_critical,
                "current_usage": monthly_usage,
                "timestamp": int(time.time())
            })
        elif monthly_usage >= monthly_warning:
            alerts.append({
                "customer_id": customer_id,
                "period": "monthly",
                "level": "warning",
                "threshold": monthly_warning,
                "current_usage": monthly_usage,
                "timestamp": int(time.time())
            })
        
        return alerts
    
    async def send_alert(self, alert: Dict[str, Any]):
        """
        Send an alert notification.
        
        Args:
            alert: Alert data
        """
        # In a real implementation, this would send an email, SMS, or other notification
        # For now, we'll just log the alert
        level = alert["level"]
        customer_id = alert["customer_id"]
        period = alert["period"]
        usage = alert["current_usage"]
        threshold = alert["threshold"]
        
        logger.warning(f"{level.upper()} ALERT: Customer {customer_id} has exceeded {period} usage threshold. Current usage: {usage}, Threshold: {threshold}")
    
    async def monitor_usage(self):
        """
        Monitor usage for all customers and send alerts.
        
        This method should be called as a background task.
        """
        while True:
            try:
                # Get all customers
                # In a real implementation, this would come from a database
                # For now, we'll use a placeholder
                customers = ["customer1", "customer2", "customer3"]
                
                # Check thresholds for each customer
                for customer_id in customers:
                    try:
                        alerts = await self.check_thresholds(customer_id)
                        
                        # Send alerts
                        for alert in alerts:
                            await self.send_alert(alert)
                    
                    except Exception as e:
                        logger.error(f"Error checking thresholds for {customer_id}: {e}")
                
                # Sleep until next check
                await asyncio.sleep(self.check_interval)
            
            except Exception as e:
                logger.error(f"Error in usage monitor: {e}")
                # Sleep for a while before retrying
                await asyncio.sleep(60)  # 1 minute

# Initialize the usage alerts service
usage_alerts = UsageAlerts()
