
"""
Registration page for the Streamlit UI.
"""
import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import show_register_form, is_authenticated, logout_user

# Set page configuration
st.set_page_config(
    page_title="Humanyze - Register",
    page_icon="🔄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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

# Check if already authenticated
if is_authenticated():
    st.success("You are already logged in!")
    st.markdown("Go to the [main page](/) to use the application.")
    
    # Show session information
    if "user" in st.session_state:
        username = st.session_state.user.get('username', 'User')
        st.info(f"Logged in as: **{username}**")
        
        # Display session time remaining if available
        from ui.auth import get_session_time_remaining
        session_time = get_session_time_remaining()
        if session_time:
            hours, minutes = session_time
            st.info(f"Session time remaining: {hours}h {minutes}m")
    
    if st.button("Logout"):
        logout_user()
        st.success("You have been logged out successfully.")
        st.rerun()
else:
    # Show registration form
    show_register_form()

# Footer
st.markdown(
    """
    <div class="footer">
        <p>© 2025 Humanyze. All rights reserved.</p>
    </div>
    """,
    unsafe_allow_html=True
)
