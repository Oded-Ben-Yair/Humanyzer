"""
Login page for the Streamlit UI.
"""
import streamlit as st
import sys
import os
import time
from urllib.parse import parse_qs
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import show_auth_ui, is_authenticated, logout_user

# Set page configuration
st.set_page_config(
    page_title="Humanyze - Login",
    page_icon="🔄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "style.css")
with open(css_path) as f:
    base_css = f.read()

# Load microinteractions CSS
microinteractions_css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "microinteractions.css")
if os.path.exists(microinteractions_css_path):
    with open(microinteractions_css_path) as f:
        microinteractions_css = f.read()
        st.markdown(f"<style>{base_css}\n{microinteractions_css}</style>", unsafe_allow_html=True)
else:
    st.markdown(f"<style>{base_css}</style>", unsafe_allow_html=True)

# Header
st.markdown(
    """
    <div class="header">
        <h1>Humanyze</h1>
        <h3>Make AI Sound Like You</h3>
    </div>
    """, 
    unsafe_allow_html=True
)

# Check for SSO callback parameters in URL
if "access_token" in st.query_params and "refresh_token" in st.query_params:
    # Store tokens in session state
    st.session_state.access_token = st.query_params["access_token"]
    st.session_state.refresh_token = st.query_params["refresh_token"]
    st.session_state.is_authenticated = True
    
    # Set token expiration times (default values if not provided)
    from datetime import datetime, timedelta
    st.session_state.access_token_expiry = (datetime.now() + timedelta(minutes=30)).timestamp()
    st.session_state.refresh_token_expiry = (datetime.now() + timedelta(days=7)).timestamp()
    st.session_state.login_time = datetime.now().timestamp()
    
    # Get user info
    from auth import get_current_user_info
    user_info = get_current_user_info()
    if user_info:
        st.session_state.user = user_info
    
    # Clear URL parameters
    st.query_params.clear()
    
    # Show success message
    st.success("SSO login successful!")
    time.sleep(1)  # Short delay for user to see the message
    st.rerun()
elif "error" in st.query_params:
    # Show error message
    error = st.query_params["error"]
    error_description = st.query_params.get("error_description", "Unknown error")
    st.error(f"SSO login failed: {error_description}")
    
    # Clear URL parameters
    st.query_params.clear()

# Check if already authenticated
if is_authenticated():
    st.success("You are already logged in!")
    st.markdown("Go to the [main page](/) to use the application.")
    
    # Show session information
    if "user" in st.session_state:
        username = st.session_state.user.get('username', 'User')
        st.info(f"Logged in as: **{username}**")
        
        # Display session time remaining if available
        from auth import get_session_time_remaining
        session_time = get_session_time_remaining()
        if session_time:
            hours, minutes = session_time
            st.info(f"Session time remaining: {hours}h {minutes}m")
    
    if st.button("Logout"):
        with st.spinner("Logging out..."):
            logout_user()
        st.success("You have been logged out successfully.")
        st.rerun()
else:
    # Show authentication UI
    show_auth_ui()

# Footer
st.markdown(
    """
    <div class="footer">
        <p>© 2025 Humanyze. All rights reserved.</p>
    </div>
    """,
    unsafe_allow_html=True
)
