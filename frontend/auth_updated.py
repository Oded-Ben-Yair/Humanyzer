"""
Authentication utilities for the Streamlit UI.
"""
import streamlit as st
import requests
import json
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

# API endpoint
API_BASE_URL = "http://localhost:8000/api"

# Token refresh settings
TOKEN_REFRESH_MARGIN_SECONDS = 300  # Refresh token 5 minutes before expiry


def register_user(username: str, email: str, password: str, confirm_password: str) -> Tuple[bool, str]:
    """
    Register a new user.
    
    Args:
        username: The username
        email: The email address
        password: The password
        confirm_password: Password confirmation
        
    Returns:
        Tuple of (success, message)
    """
    if password != confirm_password:
        return False, "Passwords do not match"
    
    try:
        with st.spinner("Creating your account..."):
            response = requests.post(
                f"{API_BASE_URL}/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "confirm_password": confirm_password
                }
            )
        
        if response.status_code == 201:
            return True, "Registration successful! Please log in."
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, f"Registration failed: {error_detail}"
    
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def login_user(email: str, password: str) -> Tuple[bool, str]:
    """
    Log in a user.
    
    Args:
        email: The email address
        password: The password
        
    Returns:
        Tuple of (success, message)
    """
    try:
        with st.spinner("Logging in..."):
            response = requests.post(
                f"{API_BASE_URL}/auth/login/email",
                json={
                    "email": email,
                    "password": password
                }
            )
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Store tokens in session state with expiration timestamps
            st.session_state.access_token = token_data["access_token"]
            st.session_state.refresh_token = token_data["refresh_token"]
            st.session_state.is_authenticated = True
            
            # Store token expiration times
            # Default expiry times if not provided by the backend
            access_token_expiry = token_data.get("access_token_expires_at", 
                                                (datetime.now() + timedelta(minutes=30)).timestamp())
            refresh_token_expiry = token_data.get("refresh_token_expires_at", 
                                                 (datetime.now() + timedelta(days=7)).timestamp())
            
            st.session_state.access_token_expiry = access_token_expiry
            st.session_state.refresh_token_expiry = refresh_token_expiry
            st.session_state.login_time = datetime.now().timestamp()
            
            # Get user info
            user_info = get_current_user_info()
            if user_info:
                st.session_state.user = user_info
            
            return True, "Login successful!"
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, f"Login failed: {error_detail}"
    
    except Exception as e:
        return False, f"Login failed: {str(e)}"


def refresh_token() -> bool:
    """
    Refresh the access token using the refresh token.
    
    Returns:
        True if successful, False otherwise
    """
    if "refresh_token" not in st.session_state:
        return False
    
    # Check if refresh token is expired
    if "refresh_token_expiry" in st.session_state:
        current_time = datetime.now().timestamp()
        if current_time >= st.session_state.refresh_token_expiry:
            logout_user()
            return False
    
    try:
        with st.spinner("Refreshing session..."):
            response = requests.post(
                f"{API_BASE_URL}/auth/refresh",
                json={"refresh_token": st.session_state.refresh_token}
            )
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Update tokens in session state
            st.session_state.access_token = token_data["access_token"]
            st.session_state.refresh_token = token_data["refresh_token"]
            st.session_state.is_authenticated = True
            
            # Update token expiration times
            access_token_expiry = token_data.get("access_token_expires_at", 
                                                (datetime.now() + timedelta(minutes=30)).timestamp())
            refresh_token_expiry = token_data.get("refresh_token_expires_at", 
                                                 (datetime.now() + timedelta(days=7)).timestamp())
            
            st.session_state.access_token_expiry = access_token_expiry
            st.session_state.refresh_token_expiry = refresh_token_expiry
            
            return True
        else:
            # Clear session state on failure
            logout_user()
            return False
    
    except Exception:
        # Clear session state on error
        logout_user()
        return False


def logout_user():
    """
    Log out the current user by revoking tokens and clearing session state.
    Calls the backend logout endpoint to invalidate tokens.
    """
    # Call backend logout endpoint if we have an access token
    if "access_token" in st.session_state:
        try:
            with st.spinner("Logging out..."):
                response = requests.post(
                    f"{API_BASE_URL}/auth/logout",
                    headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                    json={"refresh_token": st.session_state.get("refresh_token", "")}
                )
            # We don't need to check the response status as we'll clear the session anyway
        except Exception:
            # Continue with logout even if the API call fails
            pass
    
    # Clear all authentication-related session state
    if "access_token" in st.session_state:
        del st.session_state.access_token
    if "refresh_token" in st.session_state:
        del st.session_state.refresh_token
    if "user" in st.session_state:
        del st.session_state.user
    if "access_token_expiry" in st.session_state:
        del st.session_state.access_token_expiry
    if "refresh_token_expiry" in st.session_state:
        del st.session_state.refresh_token_expiry
    if "login_time" in st.session_state:
        del st.session_state.login_time
    
    st.session_state.is_authenticated = False


def check_token_expiry():
    """
    Check if the access token is about to expire and refresh it if needed.
    Should be called before making API requests.
    
    Returns:
        True if token is valid (or was refreshed), False if session expired
    """
    if "access_token" not in st.session_state or "access_token_expiry" not in st.session_state:
        return False
    
    current_time = datetime.now().timestamp()
    
    # If token is expired or about to expire, refresh it
    if current_time + TOKEN_REFRESH_MARGIN_SECONDS >= st.session_state.access_token_expiry:
        return refresh_token()
    
    return True


def get_session_time_remaining():
    """
    Get the remaining time for the current session.
    
    Returns:
        Tuple of (hours, minutes) remaining or None if not authenticated
    """
    if not is_authenticated() or "refresh_token_expiry" not in st.session_state:
        return None
    
    current_time = datetime.now().timestamp()
    remaining_seconds = max(0, st.session_state.refresh_token_expiry - current_time)
    
    remaining_hours = int(remaining_seconds // 3600)
    remaining_minutes = int((remaining_seconds % 3600) // 60)
    
    return (remaining_hours, remaining_minutes)


def get_current_user_info() -> Optional[Dict[str, Any]]:
    """
    Get information about the currently authenticated user.
    
    Returns:
        User information if authenticated, None otherwise
    """
    if "access_token" not in st.session_state:
        return None
    
    # Check token expiry and refresh if needed
    if not check_token_expiry():
        return None
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {st.session_state.access_token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            # Try to refresh the token
            if refresh_token():
                # Retry with new token
                return get_current_user_info()
            else:
                return None
        else:
            return None
    
    except Exception:
        return None


def is_authenticated() -> bool:
    """
    Check if the user is authenticated.
    
    Returns:
        True if authenticated, False otherwise
    """
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    
    if not st.session_state.is_authenticated:
        return False
    
    # Check token expiry
    if "access_token_expiry" in st.session_state:
        current_time = datetime.now().timestamp()
        if current_time >= st.session_state.access_token_expiry:
            # Try to refresh the token
            if not refresh_token():
                return False
    
    # Verify token is still valid by getting user info
    user_info = get_current_user_info()
    return user_info is not None


def auth_required(func):
    """
    Decorator to require authentication for a function.
    
    Args:
        func: The function to decorate
        
    Returns:
        Wrapped function that checks authentication
    """
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            st.warning("Please log in to access this feature.")
            show_login_form()
            return None
        return func(*args, **kwargs)
    
    return wrapper


def get_sso_providers():
    """
    Get available SSO providers from the backend.
    
    Returns:
        List of available SSO providers
    """
    try:
        response = requests.get(f"{API_BASE_URL}/auth/sso/providers")
        if response.status_code == 200:
            return response.json().get("providers", [])
        return []
    except Exception:
        return []


def show_login_form():
    """Display the login form."""
    with st.form("login_form"):
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Login", use_container_width=True)
        with col2:
            register_link = st.form_submit_button("Register", use_container_width=True)
        
        if submit:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                success, message = login_user(email, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        if register_link:
            st.session_state.show_register = True
            st.rerun()
    
    # SSO login options
    st.markdown("---")
    st.markdown("### Or sign in with")
    
    # Get available SSO providers
    providers = get_sso_providers()
    
    if providers:
        cols = st.columns(len(providers))
        for i, provider in enumerate(providers):
            with cols[i]:
                if st.button(f"{provider['name']}", key=f"sso_{provider['id']}"):
                    # Redirect to SSO login
                    redirect_uri = st.query_params.get_all().get("redirect_uri", [None])[0]
                    sso_url = f"{API_BASE_URL}/auth/sso/login/{provider['id']}"
                    if redirect_uri:
                        sso_url += f"?redirect_uri={redirect_uri}"
                    
                    # Use JavaScript to redirect
                    js = f"""
                    <script>
                    window.location.href = "{sso_url}";
                    </script>
                    """
                    st.markdown(js, unsafe_allow_html=True)
    else:
        st.info("No SSO providers available")


def show_register_form():
    """Display the registration form."""
    with st.form("register_form"):
        st.subheader("Register")
        username = st.text_input("Username", key="register_username")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("Register", use_container_width=True)
        with col2:
            login_link = st.form_submit_button("Back to Login", use_container_width=True)
        
        if submit:
            if not username or not email or not password or not confirm_password:
                st.error("Please fill in all fields.")
            else:
                success, message = register_user(username, email, password, confirm_password)
                if success:
                    st.success(message)
                    st.session_state.show_register = False
                    st.rerun()
                else:
                    st.error(message)
        
        if login_link:
            st.session_state.show_register = False
            st.rerun()


def show_auth_ui():
    """Display the authentication UI."""
    # Initialize session state
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "show_register" not in st.session_state:
        st.session_state.show_register = False
    
    # Check if already authenticated
    if is_authenticated():
        return True
    
    # Show login or register form
    if st.session_state.show_register:
        show_register_form()
    else:
        show_login_form()
    
    return False


def show_auth_status():
    """
    Display authentication status and session information.
    Should be called in the sidebar or header of the application.
    """
    if is_authenticated() and "user" in st.session_state:
        username = st.session_state.user.get('username', 'User')
        
        # Get session time remaining
        session_time = get_session_time_remaining()
        if session_time:
            hours, minutes = session_time
            time_str = f"{hours}h {minutes}m"
            
            # Determine status color based on remaining time
            if hours < 1:
                status_color = "🟠"  # Orange for less than 1 hour
            else:
                status_color = "🟢"  # Green for more than 1 hour
        else:
            time_str = "Unknown"
            status_color = "⚪"  # Gray for unknown
        
        # Display status with emoji indicator
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="font-size: 1.2em; margin-right: 5px;">{status_color}</div>
            <div>
                <div style="font-weight: bold;">{username}</div>
                <div style="font-size: 0.8em; opacity: 0.8;">Session: {time_str} remaining</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return True
    return False


def handle_auth_error(error_message: str):
    """
    Handle authentication errors with user-friendly messages.
    
    Args:
        error_message: The error message from the API
    
    Returns:
        User-friendly error message
    """
    if "rate limit" in error_message.lower():
        return "Too many login attempts. Please try again later."
    elif "token expired" in error_message.lower():
        logout_user()
        return "Your session has expired. Please log in again."
    elif "invalid token" in error_message.lower():
        logout_user()
        return "Authentication error. Please log in again."
    else:
        return error_message
