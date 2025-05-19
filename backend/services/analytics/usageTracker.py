
"""
Usage tracking service for API analytics.

This module provides functionality to track and store API usage data,
enabling usage-based billing and analytics.
"""

import time
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio
from fastapi import Request

from app.auth.redis_utils import get_redis_client
from app.config import settings

# Configure logger
logger = logging.getLogger("usage_tracker")

class UsageTracker:
    """
    Service for tracking API usage across the application.
    
    This class provides methods to record API calls, retrieve usage statistics,
    and generate reports for billing and analytics purposes.
    """
    
    def __init__(self):
        """Initialize the usage tracker with Redis connection."""
        self.redis = get_redis_client()
        self.enabled = getattr(settings, "ENABLE_USAGE_TRACKING", True)
        self.redis_prefix = getattr(settings, "REDIS_USAGE_TRACKING_PREFIX", "usage:")
        
    def _get_time_bucket(self, timestamp: Optional[int] = None) -> Dict[str, str]:
        """
        Get time bucket keys for the given timestamp.
        
        Args:
            timestamp: Unix timestamp (defaults to current time)
            
        Returns:
            Dictionary with time bucket keys (minute, hour, day, month)
        """
        if timestamp is None:
            timestamp = int(time.time())
            
        dt = datetime.fromtimestamp(timestamp)
        
        return {
            "minute": dt.strftime("%Y-%m-%d-%H-%M"),
            "hour": dt.strftime("%Y-%m-%d-%H"),
            "day": dt.strftime("%Y-%m-%d"),
            "month": dt.strftime("%Y-%m")
        }
    
    def _get_usage_key(self, customer_id: str, endpoint: str, bucket_type: str, bucket_value: str) -> str:
        """
        Generate a Redis key for usage tracking.
        
        Args:
            customer_id: Customer identifier
            endpoint: API endpoint path
            bucket_type: Time bucket type (minute, hour, day, month)
            bucket_value: Time bucket value
            
        Returns:
            Redis key string
        """
        # Normalize endpoint by removing trailing slashes and query parameters
        normalized_endpoint = endpoint.split('?')[0].rstrip('/')
        
        return f"{self.redis_prefix}{customer_id}:{normalized_endpoint}:{bucket_type}:{bucket_value}"
    
    async def track_request(self, request: Request, customer_id: str, latency_ms: Optional[float] = None) -> bool:
        """
        Track an API request.
        
        Args:
            request: FastAPI request object
            customer_id: Customer identifier
            latency_ms: Request latency in milliseconds (optional)
            
        Returns:
            True if tracking was successful, False otherwise
        """
        if not self.enabled:
            return False
            
        try:
            # Get endpoint and method
            endpoint = request.url.path
            method = request.method
            
            # Get current timestamp
            timestamp = int(time.time())
            
            # Get time buckets
            time_buckets = self._get_time_bucket(timestamp)
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()
            
            # Increment counters for each time bucket
            for bucket_type, bucket_value in time_buckets.items():
                # Increment total requests counter
                key = self._get_usage_key(customer_id, endpoint, bucket_type, bucket_value)
                pipe.hincrby(key, "count", 1)
                pipe.expire(key, self._get_expiry_seconds(bucket_type))
                
                # Increment method-specific counter
                pipe.hincrby(key, f"method:{method}", 1)
                
                # Track latency if provided
                if latency_ms is not None:
                    # Update min/max/sum for latency calculation
                    pipe.hset(key, "latency_samples", pipe.hincr(key, "latency_samples", 1))
                    
                    # Use sorted set for percentile calculations
                    latency_key = f"{key}:latency"
                    pipe.zadd(latency_key, {str(timestamp): latency_ms})
                    pipe.expire(latency_key, self._get_expiry_seconds(bucket_type))
                    
                    # Keep only the last 1000 samples for memory efficiency
                    pipe.zremrangebyrank(latency_key, 0, -1001)
            
            # Execute all commands
            pipe.execute()
            
            return True
        except Exception as e:
            logger.error(f"Error tracking API usage: {e}")
            return False
    
    def _get_expiry_seconds(self, bucket_type: str) -> int:
        """
        Get expiry time in seconds for different bucket types.
        
        Args:
            bucket_type: Time bucket type (minute, hour, day, month)
            
        Returns:
            Expiry time in seconds
        """
        if bucket_type == "minute":
            return 60 * 60 * 24  # 1 day
        elif bucket_type == "hour":
            return 60 * 60 * 24 * 7  # 1 week
        elif bucket_type == "day":
            return 60 * 60 * 24 * 30  # 30 days
        elif bucket_type == "month":
            return 60 * 60 * 24 * 365  # 1 year
        else:
            return 60 * 60 * 24 * 7  # Default: 1 week
    
    async def get_usage_stats(
        self, 
        customer_id: str, 
        start_time: datetime,
        end_time: Optional[datetime] = None,
        endpoint: Optional[str] = None,
        bucket_type: str = "day"
    ) -> Dict[str, Any]:
        """
        Get usage statistics for a customer.
        
        Args:
            customer_id: Customer identifier
            start_time: Start time for the report
            end_time: End time for the report (defaults to current time)
            endpoint: Filter by specific endpoint (optional)
            bucket_type: Time bucket type (minute, hour, day, month)
            
        Returns:
            Dictionary with usage statistics
        """
        if not self.enabled:
            return {"error": "Usage tracking is disabled"}
            
        try:
            # Set default end time to now if not provided
            if end_time is None:
                end_time = datetime.now()
                
            # Initialize results
            results = {
                "customer_id": customer_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "bucket_type": bucket_type,
                "total_requests": 0,
                "endpoints": {},
                "methods": {
                    "GET": 0,
                    "POST": 0,
                    "PUT": 0,
                    "DELETE": 0,
                    "PATCH": 0
                }
            }
            
            # Generate time buckets for the date range
            current_time = start_time
            time_buckets = []
            
            while current_time <= end_time:
                bucket_value = None
                
                if bucket_type == "minute":
                    bucket_value = current_time.strftime("%Y-%m-%d-%H-%M")
                    current_time += timedelta(minutes=1)
                elif bucket_type == "hour":
                    bucket_value = current_time.strftime("%Y-%m-%d-%H")
                    current_time += timedelta(hours=1)
                elif bucket_type == "day":
                    bucket_value = current_time.strftime("%Y-%m-%d")
                    current_time += timedelta(days=1)
                elif bucket_type == "month":
                    bucket_value = current_time.strftime("%Y-%m")
                    # Move to the first day of next month
                    if current_time.month == 12:
                        current_time = datetime(current_time.year + 1, 1, 1)
                    else:
                        current_time = datetime(current_time.year, current_time.month + 1, 1)
                
                if bucket_value:
                    time_buckets.append(bucket_value)
            
            # Get all endpoints if not specified
            endpoints_to_check = [endpoint] if endpoint else await self._get_customer_endpoints(customer_id)
            
            # Collect data for each endpoint and time bucket
            for ep in endpoints_to_check:
                endpoint_total = 0
                endpoint_data = {
                    "total": 0,
                    "by_date": {}
                }
                
                for bucket_value in time_buckets:
                    key = self._get_usage_key(customer_id, ep, bucket_type, bucket_value)
                    
                    # Get all data for this key
                    data = self.redis.hgetall(key)
                    
                    if data:
                        # Extract count
                        count = int(data.get("count", 0))
                        endpoint_total += count
                        
                        # Add to endpoint data
                        endpoint_data["by_date"][bucket_value] = count
                        
                        # Add to methods totals
                        for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                            method_count = int(data.get(f"method:{method}", 0))
                            results["methods"][method] += method_count
                
                # Add endpoint total
                endpoint_data["total"] = endpoint_total
                results["total_requests"] += endpoint_total
                
                # Add to results
                if endpoint_total > 0:
                    results["endpoints"][ep] = endpoint_data
            
            return results
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return {"error": str(e)}
    
    async def _get_customer_endpoints(self, customer_id: str) -> List[str]:
        """
        Get all endpoints used by a customer.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            List of endpoint paths
        """
        try:
            # Use Redis scan to find all keys for this customer
            pattern = f"{self.redis_prefix}{customer_id}:*"
            endpoints = set()
            
            # Scan for keys matching the pattern
            cursor = 0
            while True:
                cursor, keys = self.redis.scan(cursor, match=pattern, count=100)
                
                for key in keys:
                    # Extract endpoint from key
                    parts = key.split(':')
                    if len(parts) >= 3:
                        endpoint = parts[2]
                        endpoints.add(endpoint)
                
                if cursor == 0:
                    break
            
            return list(endpoints)
        except Exception as e:
            logger.error(f"Error getting customer endpoints: {e}")
            return []
    
    async def generate_usage_report(
        self,
        customer_id: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        format: str = "json"
    ) -> str:
        """
        Generate a usage report for a customer.
        
        Args:
            customer_id: Customer identifier
            start_time: Start time for the report
            end_time: End time for the report (defaults to current time)
            format: Report format (json or csv)
            
        Returns:
            Report data in the specified format
        """
        # Get usage statistics
        stats = await self.get_usage_stats(
            customer_id=customer_id,
            start_time=start_time,
            end_time=end_time,
            bucket_type="day"
        )
        
        if "error" in stats:
            return json.dumps({"error": stats["error"]})
        
        if format.lower() == "json":
            return json.dumps(stats, indent=2)
        elif format.lower() == "csv":
            # Generate CSV
            csv_lines = ["Date,Endpoint,Requests"]
            
            for endpoint, data in stats["endpoints"].items():
                for date, count in data["by_date"].items():
                    csv_lines.append(f"{date},{endpoint},{count}")
            
            return "\n".join(csv_lines)
        else:
            return json.dumps({"error": f"Unsupported format: {format}"})
    
    async def get_customer_usage_summary(self, customer_id: str) -> Dict[str, Any]:
        """
        Get a summary of usage for a customer.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            Dictionary with usage summary
        """
        # Get current time
        now = datetime.now()
        
        # Get usage for different time periods
        today = await self.get_usage_stats(
            customer_id=customer_id,
            start_time=datetime(now.year, now.month, now.day),
            end_time=now,
            bucket_type="hour"
        )
        
        this_month = await self.get_usage_stats(
            customer_id=customer_id,
            start_time=datetime(now.year, now.month, 1),
            end_time=now,
            bucket_type="day"
        )
        
        # Calculate month-to-date and projected monthly usage
        days_in_month = (datetime(now.year, now.month % 12 + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)) - datetime(now.year, now.month, 1)
        days_so_far = now.day
        
        mtd_requests = this_month.get("total_requests", 0)
        projected_requests = int(mtd_requests * (days_in_month.days / days_so_far)) if days_so_far > 0 else 0
        
        return {
            "customer_id": customer_id,
            "current_time": now.isoformat(),
            "today_requests": today.get("total_requests", 0),
            "month_to_date_requests": mtd_requests,
            "projected_monthly_requests": projected_requests,
            "top_endpoints": self._get_top_endpoints(this_month, 5)
        }
    
    def _get_top_endpoints(self, usage_stats: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top endpoints by request count.
        
        Args:
            usage_stats: Usage statistics dictionary
            limit: Maximum number of endpoints to return
            
        Returns:
            List of top endpoints with counts
        """
        endpoints = []
        
        for endpoint, data in usage_stats.get("endpoints", {}).items():
            endpoints.append({
                "endpoint": endpoint,
                "requests": data.get("total", 0)
            })
        
        # Sort by request count (descending)
        endpoints.sort(key=lambda x: x["requests"], reverse=True)
        
        # Return top N
        return endpoints[:limit]

# Initialize the usage tracker
usage_tracker = UsageTracker()
