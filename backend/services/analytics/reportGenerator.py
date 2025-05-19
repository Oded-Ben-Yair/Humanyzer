
"""
Report generator for API usage analytics.

This module provides functionality to generate scheduled reports
for API usage and billing purposes.
"""

import logging
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
import csv
import io
from pathlib import Path

from app.services.analytics.usageTracker import usage_tracker
from app.config import settings

# Configure logger
logger = logging.getLogger("report_generator")

class ReportGenerator:
    """
    Service for generating scheduled usage reports.
    
    This class provides methods to generate and export usage reports
    for billing and analytics purposes.
    """
    
    def __init__(self):
        """Initialize the report generator."""
        self.reports_dir = getattr(settings, "USAGE_REPORTS_DIR", "reports")
        
        # Create reports directory if it doesn't exist
        os.makedirs(self.reports_dir, exist_ok=True)
    
    async def generate_daily_report(self, customer_id: str) -> str:
        """
        Generate a daily usage report for a customer.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            Path to the generated report file
        """
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        start_time = datetime(yesterday.year, yesterday.month, yesterday.day)
        end_time = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
        
        # Generate report filename
        filename = f"{customer_id}_daily_{yesterday.strftime('%Y-%m-%d')}.csv"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Get usage statistics
        stats = await usage_tracker.get_usage_stats(
            customer_id=customer_id,
            start_time=start_time,
            end_time=end_time,
            bucket_type="hour"
        )
        
        # Write CSV report
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Hour", "Endpoint", "Requests", "GET", "POST", "PUT", "DELETE", "PATCH"])
            
            for endpoint, data in stats.get("endpoints", {}).items():
                for hour, count in data.get("by_date", {}).items():
                    # Get method breakdown
                    methods = {}
                    for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                        methods[method] = stats.get("methods", {}).get(method, 0)
                    
                    writer.writerow([
                        hour,
                        endpoint,
                        count,
                        methods.get("GET", 0),
                        methods.get("POST", 0),
                        methods.get("PUT", 0),
                        methods.get("DELETE", 0),
                        methods.get("PATCH", 0)
                    ])
        
        logger.info(f"Generated daily report for customer {customer_id}: {filepath}")
        return filepath
    
    async def generate_monthly_report(self, customer_id: str, month: Optional[int] = None, year: Optional[int] = None) -> str:
        """
        Generate a monthly usage report for a customer.
        
        Args:
            customer_id: Customer identifier
            month: Month number (1-12, defaults to previous month)
            year: Year (defaults to current year)
            
        Returns:
            Path to the generated report file
        """
        # Set default month and year if not provided
        now = datetime.now()
        
        if month is None:
            # Default to previous month
            if now.month == 1:
                month = 12
                year = now.year - 1
            else:
                month = now.month - 1
                year = now.year
        
        if year is None:
            year = now.year
        
        # Calculate start and end dates
        start_time = datetime(year, month, 1)
        
        # Calculate end of month
        if month == 12:
            end_time = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_time = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Generate report filename
        filename = f"{customer_id}_monthly_{year}-{month:02d}.csv"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Get usage statistics
        stats = await usage_tracker.get_usage_stats(
            customer_id=customer_id,
            start_time=start_time,
            end_time=end_time,
            bucket_type="day"
        )
        
        # Write CSV report
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Date", "Endpoint", "Requests", "GET", "POST", "PUT", "DELETE", "PATCH"])
            
            for endpoint, data in stats.get("endpoints", {}).items():
                for date, count in data.get("by_date", {}).items():
                    # Get method breakdown
                    methods = {}
                    for method in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                        methods[method] = stats.get("methods", {}).get(method, 0)
                    
                    writer.writerow([
                        date,
                        endpoint,
                        count,
                        methods.get("GET", 0),
                        methods.get("POST", 0),
                        methods.get("PUT", 0),
                        methods.get("DELETE", 0),
                        methods.get("PATCH", 0)
                    ])
        
        logger.info(f"Generated monthly report for customer {customer_id}: {filepath}")
        return filepath
    
    async def export_report(self, stats: Dict[str, Any], format: str = "csv") -> str:
        """
        Export usage statistics to a file.
        
        Args:
            stats: Usage statistics dictionary
            format: Export format (csv or json)
            
        Returns:
            File content as string
        """
        if format.lower() == "json":
            return json.dumps(stats, indent=2)
        elif format.lower() == "csv":
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(["Date", "Endpoint", "Requests"])
            
            # Write data
            for endpoint, data in stats.get("endpoints", {}).items():
                for date, count in data.get("by_date", {}).items():
                    writer.writerow([date, endpoint, count])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def schedule_daily_reports(self):
        """
        Schedule daily reports for all customers.
        
        This method should be called as a background task.
        """
        while True:
            try:
                # Get current time
                now = datetime.now()
                
                # Calculate time until next run (1:00 AM)
                next_run = datetime(now.year, now.month, now.day, 1, 0, 0)
                if now >= next_run:
                    next_run = next_run + timedelta(days=1)
                
                # Sleep until next run
                sleep_seconds = (next_run - now).total_seconds()
                logger.info(f"Scheduling daily reports to run in {sleep_seconds} seconds")
                await asyncio.sleep(sleep_seconds)
                
                # Get all customers
                # In a real implementation, this would come from a database
                # For now, we'll use a placeholder
                customers = ["customer1", "customer2", "customer3"]
                
                # Generate reports for each customer
                for customer_id in customers:
                    try:
                        await self.generate_daily_report(customer_id)
                    except Exception as e:
                        logger.error(f"Error generating daily report for {customer_id}: {e}")
            
            except Exception as e:
                logger.error(f"Error in daily report scheduler: {e}")
                # Sleep for a while before retrying
                await asyncio.sleep(3600)  # 1 hour

# Initialize the report generator
report_generator = ReportGenerator()
