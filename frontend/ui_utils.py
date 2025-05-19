
"""
Utility functions for the Humanyze UI to communicate with the API.
"""
import requests
import json
import os
from typing import Dict, Any, Optional

# API base URL - adjust as needed for your environment
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")

def get_api_url():
    """Get the API base URL."""
    return API_BASE_URL

def humanize_text(text: str, style: str = "casual", profile_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Send a request to the humanize endpoint to transform text.
    
    Args:
        text: The text to humanize
        style: The writing style to use (casual, professional, creative)
        profile_id: ID of the style profile to use (optional)
        
    Returns:
        The API response as a dictionary, or None if the request failed
    """
    try:
        request_data = {"text": text, "style": style}
        if profile_id:
            request_data["profile_id"] = profile_id
            
        response = requests.post(
            f"{API_BASE_URL}/humanize",
            json=request_data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def humanize_text_async(text: str, style: str = "casual", profile_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Send a request to the async humanize endpoint to transform text.
    
    Args:
        text: The text to humanize
        style: The writing style to use (casual, professional, creative)
        profile_id: ID of the style profile to use (optional)
        
    Returns:
        The API response with job ID, or None if the request failed
    """
    try:
        request_data = {"text": text, "style": style}
        if profile_id:
            request_data["profile_id"] = profile_id
            
        response = requests.post(
            f"{API_BASE_URL}/humanize/async",
            json=request_data
        )
        
        if response.status_code == 202:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def get_humanize_status(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Check the status of an asynchronous humanization job.
    
    Args:
        job_id: The ID of the job to check
        
    Returns:
        The API response with job status, or None if the request failed
    """
    try:
        response = requests.get(f"{API_BASE_URL}/humanize/status/{job_id}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def analyze_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Send a request to the analyze endpoint to analyze text.
    
    Args:
        text: The text to analyze
        
    Returns:
        The API response as a dictionary, or None if the request failed
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json={"text": text}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def get_profiles() -> Optional[Dict[str, Any]]:
    """
    Get all style profiles.
    
    Returns:
        The API response as a dictionary, or None if the request failed
    """
    try:
        response = requests.get(f"{API_BASE_URL}/profiles")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def get_profile(profile_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a style profile by ID.
    
    Args:
        profile_id: ID of the profile to get
        
    Returns:
        The API response as a dictionary, or None if the request failed
    """
    try:
        response = requests.get(f"{API_BASE_URL}/profiles/{profile_id}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def create_profile(profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create a new style profile.
    
    Args:
        profile_data: Profile data to create
        
    Returns:
        The API response as a dictionary, or None if the request failed
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/profiles",
            json=profile_data
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def update_profile(profile_id: str, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update an existing style profile.
    
    Args:
        profile_id: ID of the profile to update
        profile_data: Updated profile data
        
    Returns:
        The API response as a dictionary, or None if the request failed
    """
    try:
        response = requests.put(
            f"{API_BASE_URL}/profiles/{profile_id}",
            json=profile_data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def delete_profile(profile_id: str) -> bool:
    """
    Delete a style profile.
    
    Args:
        profile_id: ID of the profile to delete
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        response = requests.delete(f"{API_BASE_URL}/profiles/{profile_id}")
        
        if response.status_code == 204:
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return False



def get_subscription(auth_header: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """
    Get the current user's subscription.
    
    Args:
        auth_header: Authentication header
        
    Returns:
        The API response as a dictionary, or None if the request failed
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/payments/subscription",
            headers=auth_header
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def get_subscription_plans() -> Optional[Dict[str, Any]]:
    """
    Get available subscription plans.
    
    Returns:
        The API response as a dictionary, or None if the request failed
    """
    try:
        response = requests.get(f"{API_BASE_URL}/payments/plans")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def create_checkout_session(
    auth_header: Dict[str, str],
    price_id: str,
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a Stripe checkout session.
    
    Args:
        auth_header: Authentication header
        price_id: Stripe Price ID
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect after cancelled payment
        metadata: Additional metadata
        
    Returns:
        The API response as a dictionary, or None if the request failed
    """
    try:
        request_data = {
            "price_id": price_id
        }
        
        if success_url:
            request_data["success_url"] = success_url
        
        if cancel_url:
            request_data["cancel_url"] = cancel_url
        
        if metadata:
            request_data["metadata"] = metadata
        
        response = requests.post(
            f"{API_BASE_URL}/payments/create-checkout-session",
            headers=auth_header,
            json=request_data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def create_customer_portal(
    auth_header: Dict[str, str],
    return_url: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Create a Stripe customer portal session.
    
    Args:
        auth_header: Authentication header
        return_url: URL to return to after using the portal
        
    Returns:
        The API response as a dictionary, or None if the request failed
    """
    try:
        request_data = {}
        
        if return_url:
            request_data["return_url"] = return_url
        
        response = requests.post(
            f"{API_BASE_URL}/payments/create-customer-portal",
            headers=auth_header,
            json=request_data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None

def check_subscription_limit(
    auth_header: Dict[str, str],
    character_count: int = 0
) -> Optional[Dict[str, Any]]:
    """
    Check if user has reached subscription limits.
    
    Args:
        auth_header: Authentication header
        character_count: Number of characters to check
        
    Returns:
        The API response as a dictionary, or None if the request failed
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/payments/subscription/check-limit?character_count={character_count}",
            headers=auth_header
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request failed: {str(e)}")
        return None
