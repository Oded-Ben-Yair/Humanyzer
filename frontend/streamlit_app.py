"""
Streamlit application for the Humanyze MVP.
"""
import streamlit as st
import json
import sys
import os
from pathlib import Path
# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui_utils import (
    humanize_text, 
    analyze_text, 
    get_humanize_status,
    humanize_text_async,
    get_profiles,
    create_profile,
    update_profile,
    delete_profile,
    get_profile
)
from auth import (
    is_authenticated,
    show_auth_ui,
    logout_user,
    auth_required,
    show_auth_status,
    check_token_expiry,
    get_session_time_remaining,
    handle_auth_error
)
from healthcheck import initialize_health_check

# Set page configuration
st.set_page_config(
    page_title="Humanyze - Make AI Sound Like You",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize health check endpoint for load balancer
initialize_health_check()

# Load custom CSS
import os
# Load base styles
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        base_css = f.read()

# Load mobile responsive styles
mobile_css_path = os.path.join(os.path.dirname(__file__), "mobile.css")
if os.path.exists(mobile_css_path):
    with open(mobile_css_path) as f:
        mobile_css = f.read()

# Load microinteractions CSS
microinteractions_css_path = os.path.join(os.path.dirname(__file__), "microinteractions.css")
if os.path.exists(microinteractions_css_path):
    with open(microinteractions_css_path) as f:
        microinteractions_css = f.read()

# Load workspace CSS
workspace_css_path = os.path.join(os.path.dirname(__file__), "workspace.css")
if os.path.exists(workspace_css_path):
    with open(workspace_css_path) as f:
        workspace_css = f.read()
        # Combine and apply all styles
        st.markdown(f"<style>{base_css}\n{mobile_css}\n{microinteractions_css}\n{workspace_css}</style>", unsafe_allow_html=True)
else:
    # Combine and apply base, mobile, and microinteractions styles
    st.markdown(f"<style>{base_css}\n{mobile_css}\n{microinteractions_css}</style>", unsafe_allow_html=True)

# Load mobile JavaScript enhancements
mobile_js_path = os.path.join(os.path.dirname(__file__), "mobile.js")
if os.path.exists(mobile_js_path):
    with open(mobile_js_path) as f:
        mobile_js = f.read()
        st.components.v1.html(f"<script>{mobile_js}</script>", height=0)

# Initialize UI enhancements from components
try:
    from components.common import initialize_ui_enhancements
    initialize_ui_enhancements()
except ImportError:
    # If components are not available, continue without them
    pass

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

# Check token expiry before any authenticated operations
if "is_authenticated" in st.session_state and st.session_state.is_authenticated:
    check_token_expiry()

# Authentication check
authenticated = is_authenticated()

# Show login/logout in the sidebar
with st.sidebar:
    st.markdown("### Account")
    
    if authenticated:
        # Show authentication status with visual indicator
        show_auth_status()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Subscription", key="subscription_button"):
                st.switch_page("pages/subscription.py")
        
        with col2:
            if st.button("Logout", key="logout_button"):
                with st.spinner("Logging out..."):
                    logout_user()
                st.success("You have been logged out successfully.")
                st.rerun()
    else:
        st.warning("You are not logged in.")
        if st.button("Login", key="login_button"):
            st.switch_page("pages/login_updated.py")
        if st.button("Register", key="register_button"):
            st.switch_page("pages/register.py")

# Initialize session state
if 'original_text' not in st.session_state:
    st.session_state.original_text = ""
if 'humanized_text' not in st.session_state:
    st.session_state.humanized_text = ""
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'job_status' not in st.session_state:
    st.session_state.job_status = None
if 'profiles' not in st.session_state:
    st.session_state.profiles = []
if 'selected_profile_id' not in st.session_state:
    st.session_state.selected_profile_id = None
if 'show_profile_editor' not in st.session_state:
    st.session_state.show_profile_editor = False
if 'edit_profile_id' not in st.session_state:
    st.session_state.edit_profile_id = None
if 'auth_errors' not in st.session_state:
    st.session_state.auth_errors = []

# Display auth errors if any
if st.session_state.auth_errors:
    for error in st.session_state.auth_errors:
        st.error(error)
    # Clear errors after displaying
    st.session_state.auth_errors = []

# Load profiles
def load_profiles():
    try:
        with st.spinner("Loading profiles..."):
            profiles_response = get_profiles()
            if profiles_response and "profiles" in profiles_response:
                st.session_state.profiles = profiles_response["profiles"]
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "token" in error_msg.lower():
            # Handle auth error
            st.session_state.auth_errors.append(handle_auth_error(error_msg))
            st.rerun()
        else:
            st.error(f"Error loading profiles: {error_msg}")

# Load profiles on startup
if authenticated and not st.session_state.profiles:
    load_profiles()

# Sidebar for style profiles
with st.sidebar:
    st.markdown("### Style Profiles")
    
    # Profile selection
    profile_options = ["None (Use Basic Style)"] + [f"{p['name']}" for p in st.session_state.profiles]
    profile_indices = {p["id"]: i+1 for i, p in enumerate(st.session_state.profiles)}
    
    selected_index = 0
    if st.session_state.selected_profile_id:
        selected_index = profile_indices.get(st.session_state.selected_profile_id, 0)
    
    selected_profile = st.selectbox(
        "Select a style profile:",
        options=profile_options,
        index=selected_index
    )
    
    # Update selected profile ID
    if selected_profile == "None (Use Basic Style)":
        st.session_state.selected_profile_id = None
    else:
        for profile in st.session_state.profiles:
            if profile["name"] == selected_profile:
                st.session_state.selected_profile_id = profile["id"]
                break
    
    # Profile management buttons - only show if authenticated
    if authenticated:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("New Profile", use_container_width=True):
                st.session_state.show_profile_editor = True
                st.session_state.edit_profile_id = None
        
        with col2:
            if st.session_state.selected_profile_id and st.button("Edit Profile", use_container_width=True):
                st.session_state.show_profile_editor = True
                st.session_state.edit_profile_id = st.session_state.selected_profile_id
    else:
        st.info("Log in to create and edit profiles.")
    
    # Profile editor
    if st.session_state.show_profile_editor and authenticated:
        st.markdown("### Profile Editor")
        
        # Initialize with existing profile data if editing
        profile_data = {}
        if st.session_state.edit_profile_id:
            for profile in st.session_state.profiles:
                if profile["id"] == st.session_state.edit_profile_id:
                    profile_data = profile
                    break
        
        # Profile form with improved mobile responsiveness
        with st.form("profile_form"):
            st.markdown('<div class="profile-form-section basic-info">', unsafe_allow_html=True)
            name = st.text_input("Profile Name", 
                                value=profile_data.get("name", ""),
                                placeholder="Enter a descriptive name")
            description = st.text_area("Description", 
                                      value=profile_data.get("description", ""),
                                      placeholder="Describe the purpose of this profile",
                                      height=100)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="profile-form-section base-settings">', unsafe_allow_html=True)
            st.markdown("#### Base Settings")
            base_style = st.selectbox(
                "Base Style",
                options=["casual", "professional", "creative"],
                index=["casual", "professional", "creative"].index(profile_data.get("base_style", "casual"))
            )
            
            tone = st.text_input("Tone", 
                               value=profile_data.get("tone", "neutral"),
                               placeholder="e.g., friendly, authoritative, enthusiastic")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="profile-form-section style-params">', unsafe_allow_html=True)
            st.markdown("#### Style Parameters")
            
            # On mobile, these will stack naturally
            col1, col2 = st.columns(2)
            
            with col1:
                formality_level = st.slider(
                    "Formality Level",
                    min_value=1,
                    max_value=10,
                    value=profile_data.get("formality_level", 5),
                    help="1 = Very informal, 10 = Very formal"
                )
                
                contraction_probability = st.slider(
                    "Contraction Probability",
                    min_value=0.0,
                    max_value=1.0,
                    value=float(profile_data.get("contraction_probability", 0.7)),
                    step=0.1,
                    help="Probability of using contractions (0.0-1.0)"
                )
            
            with col2:
                conversational_element_frequency = st.slider(
                    "Conversational Element Frequency",
                    min_value=1,
                    max_value=10,
                    value=profile_data.get("conversational_element_frequency", 4),
                    help="Higher = less frequent"
                )
                
                sentence_variation_level = st.slider(
                    "Sentence Variation Level",
                    min_value=1,
                    max_value=10,
                    value=profile_data.get("sentence_variation_level", 5),
                    help="1 = Minimal variation, 10 = Maximum variation"
                )
            
            vocabulary_richness = st.slider(
                "Vocabulary Richness",
                min_value=1,
                max_value=10,
                value=profile_data.get("vocabulary_richness", 5),
                help="1 = Simple vocabulary, 10 = Rich vocabulary"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="profile-form-section advanced-settings">', unsafe_allow_html=True)
            st.markdown("#### Advanced Settings")
            custom_phrases_text = "\n".join(profile_data.get("custom_phrases", []))
            custom_phrases = st.text_area(
                "Custom Phrases (one per line)",
                value=custom_phrases_text,
                help="Phrases to incorporate into the text",
                placeholder="Enter phrases to include, one per line",
                height=100
            )
            
            avoid_phrases_text = "\n".join(profile_data.get("avoid_phrases", []))
            avoid_phrases = st.text_area(
                "Phrases to Avoid (one per line)",
                value=avoid_phrases_text,
                help="Phrases to avoid in the text",
                placeholder="Enter phrases to avoid, one per line",
                height=100
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Submit buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                submit = st.form_submit_button("Save Profile")
            
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            with col3:
                if st.session_state.edit_profile_id:
                    delete = st.form_submit_button("Delete Profile")
                else:
                    delete = False
        
        # Handle form submission
        if submit:
            try:
                # Prepare profile data
                profile_data = {
                    "name": name,
                    "description": description,
                    "base_style": base_style,
                    "tone": tone,
                    "formality_level": formality_level,
                    "contraction_probability": contraction_probability,
                    "conversational_element_frequency": conversational_element_frequency,
                    "sentence_variation_level": sentence_variation_level,
                    "vocabulary_richness": vocabulary_richness,
                    "custom_phrases": [p.strip() for p in custom_phrases.split("\n") if p.strip()],
                    "avoid_phrases": [p.strip() for p in avoid_phrases.split("\n") if p.strip()]
                }
                
                if st.session_state.edit_profile_id:
                    # Update existing profile
                    with st.spinner("Updating profile..."):
                        response = update_profile(st.session_state.edit_profile_id, profile_data)
                    if response:
                        st.success(f"Profile '{name}' updated successfully!")
                else:
                    # Create new profile
                    with st.spinner("Creating profile..."):
                        response = create_profile(profile_data)
                    if response:
                        st.success(f"Profile '{name}' created successfully!")
                        st.session_state.selected_profile_id = response.get("id")
                
                # Reload profiles and close editor
                load_profiles()
                st.session_state.show_profile_editor = False
                st.session_state.edit_profile_id = None
                st.rerun()
                
            except Exception as e:
                error_msg = str(e)
                if "401" in error_msg or "token" in error_msg.lower():
                    # Handle auth error
                    st.session_state.auth_errors.append(handle_auth_error(error_msg))
                    st.rerun()
                else:
                    st.error(f"Error saving profile: {error_msg}")
        
        if cancel:
            st.session_state.show_profile_editor = False
            st.session_state.edit_profile_id = None
            st.rerun()
        
        if delete and st.session_state.edit_profile_id:
            try:
                with st.spinner("Deleting profile..."):
                    response = delete_profile(st.session_state.edit_profile_id)
                if response:
                    st.success(f"Profile '{name}' deleted successfully!")
                
                # Reset selection and reload profiles
                st.session_state.selected_profile_id = None
                load_profiles()
                st.session_state.show_profile_editor = False
                st.session_state.edit_profile_id = None
                st.rerun()
                
            except Exception as e:
                error_msg = str(e)
                if "401" in error_msg or "token" in error_msg.lower():
                    # Handle auth error
                    st.session_state.auth_errors.append(handle_auth_error(error_msg))
                    st.rerun()
                else:
                    st.error(f"Error deleting profile: {error_msg}")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Transform Content", "Analysis Results", "About"])

# Tab 1: Transform Content
with tab1:
    st.markdown("### Transform Your AI-Generated Content")
    
    # Check authentication
    if not authenticated:
        st.warning("Please log in to use this feature.")
        st.info("Use the login button in the sidebar to access your account.")
    else:
        # Text input area with mobile-friendly container
        st.markdown('<div class="text-input-container">', unsafe_allow_html=True)
        text_input = st.text_area(
            "Paste your AI-generated text here:",
            height=250,
            key="text_input",
            value=st.session_state.original_text if st.session_state.original_text else "",
            placeholder="Enter or paste your AI-generated text here. The more text you provide, the better the transformation will be."
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Options with responsive layout
        st.markdown('<div class="options-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="style-selector">', unsafe_allow_html=True)
            style = st.selectbox(
                "Select writing style:",
                options=["casual", "professional", "creative"],
                index=0
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="process-mode-selector">', unsafe_allow_html=True)
            process_mode = st.radio(
                "Processing mode:",
                options=["Synchronous", "Asynchronous"],
                index=0,
                horizontal=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit button
        if st.button("Humanize Text", type="primary", use_container_width=True):
            if not text_input or not text_input.strip():
                st.error("Please enter some text to humanize.")
            else:
                st.session_state.original_text = text_input
                
                # Check token expiry before making API request
                if not check_token_expiry():
                    st.session_state.auth_errors.append("Your session has expired. Please log in again.")
                    st.rerun()
                
                with st.spinner("Transforming your text..."):
                    try:
                        if process_mode == "Synchronous":
                            # Synchronous processing
                            response = humanize_text(text_input, style, st.session_state.selected_profile_id)
                            
                            if response:
                                st.session_state.humanized_text = response.get("humanized", "")
                                st.session_state.analysis = response.get("analysis", None)
                                st.success("Text transformed successfully!")
                                
                                # Switch to results tab
                                st.rerun()
                        else:
                            # Asynchronous processing
                            response = humanize_text_async(text_input, style, st.session_state.selected_profile_id)
                            
                            if response:
                                st.session_state.job_id = response.get("job_id")
                                st.session_state.job_status = response.get("status")
                                st.info(f"Job submitted successfully! Job ID: {st.session_state.job_id}")
                                st.info("Check the Analysis Results tab for status updates.")
                    except Exception as e:
                        error_msg = str(e)
                        if "401" in error_msg or "token" in error_msg.lower():
                            # Handle auth error
                            st.session_state.auth_errors.append(handle_auth_error(error_msg))
                            st.rerun()
                        else:
                            st.error(f"Error processing text: {error_msg}")

# Tab 2: Analysis Results
with tab2:
    st.markdown("### Results")
    
    # Check authentication
    if not authenticated:
        st.warning("Please log in to view analysis results.")
        st.info("Use the login button in the sidebar to access your account.")
    else:
        # Check if we have a job ID and it's still processing
        if st.session_state.job_id and st.session_state.job_status == "processing":
            if st.button("Check Job Status"):
                # Check token expiry before making API request
                if not check_token_expiry():
                    st.session_state.auth_errors.append("Your session has expired. Please log in again.")
                    st.rerun()
                
                with st.spinner("Checking job status..."):
                    try:
                        job_response = get_humanize_status(st.session_state.job_id)
                        
                        if job_response:
                            st.session_state.job_status = job_response.get("status")
                            
                            if job_response.get("status") == "completed":
                                result = job_response.get("result", {})
                                st.session_state.humanized_text = result.get("humanized", "")
                                st.session_state.analysis = result.get("analysis", None)
                                st.success("Text transformation completed!")
                            elif job_response.get("status") == "failed":
                                st.error(f"Job failed: {job_response.get('error', 'Unknown error')}")
                            else:
                                st.info(f"Job is still processing. Status: {job_response.get('status')}")
                    except Exception as e:
                        error_msg = str(e)
                        if "401" in error_msg or "token" in error_msg.lower():
                            # Handle auth error
                            st.session_state.auth_errors.append(handle_auth_error(error_msg))
                            st.rerun()
                        else:
                            st.error(f"Error checking job status: {error_msg}")
    
        # Display results if available
        if st.session_state.humanized_text:
            # Responsive text comparison - stacks on mobile, side-by-side on desktop
            st.markdown("""
            <div class="text-comparison-container">
                <h4>Text Comparison</h4>
                <p class="text-comparison-note">Compare the original AI-generated text with the humanized version.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="text-comparison original">', unsafe_allow_html=True)
                st.markdown("#### Original Text")
                st.text_area(
                    "Original",
                    value=st.session_state.original_text,
                    height=300,
                    disabled=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="text-comparison humanized">', unsafe_allow_html=True)
                st.markdown("#### Humanized Text")
                st.text_area(
                    "Humanized",
                    value=st.session_state.humanized_text,
                    height=300,
                    disabled=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Display analysis if available with improved mobile responsiveness
            if st.session_state.analysis:
                st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
                st.markdown('<h4 class="analysis-title">Analysis Results</h4>', unsafe_allow_html=True)
                
                # AI likelihood
                is_likely_ai = st.session_state.analysis.get("is_likely_ai", False)
                ai_likelihood = "High" if is_likely_ai else "Low"
                likelihood_color = "var(--danger-color)" if is_likely_ai else "var(--success-color)"
                
                st.markdown(
                    f"""
                    <div class='ai-likelihood-container'>
                        <h5>AI Detection Risk</h5>
                        <div class='likelihood-indicator'>
                            <span class='likelihood-label'>AI Likelihood:</span>
                            <span class='likelihood-value' style='color:{likelihood_color};'>{ai_likelihood}</span>
                        </div>
                        <p class='likelihood-explanation'>
                            {
                                "Your text may still be detectable as AI-generated. Consider further refinements." 
                                if is_likely_ai else 
                                "Your text now appears more human-like and is less likely to be detected as AI-generated."
                            }
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Metrics with responsive layout
                metrics = st.session_state.analysis.get("metrics", {})
                if metrics:
                    st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
                    st.markdown('<h5>Text Metrics</h5>', unsafe_allow_html=True)
                    
                    # On mobile these will stack automatically
                    metric_cols = st.columns(3)
                    
                    with metric_cols[0]:
                        st.metric(
                            "Avg. Sentence Length", 
                            f"{metrics.get('avg_sentence_length', 0):.1f} words",
                            delta=None,
                            delta_color="off"
                        )
                    
                    with metric_cols[1]:
                        st.metric(
                            "Repeated N-grams", 
                            metrics.get("repeated_ngrams_count", 0),
                            delta=None,
                            delta_color="off"
                        )
                    
                    with metric_cols[2]:
                        st.metric(
                            "Contraction Ratio", 
                            f"{metrics.get('contraction_ratio', 0):.2f}",
                            delta=None,
                            delta_color="off"
                        )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Patterns found with improved mobile layout
                patterns = st.session_state.analysis.get("patterns_found", [])
                if patterns:
                    st.markdown('<div class="patterns-container">', unsafe_allow_html=True)
                    st.markdown('<h5>Detected Patterns</h5>', unsafe_allow_html=True)
                    
                    for pattern in patterns:
                        severity = pattern.get("severity", "low")
                        severity_color = {
                            "low": "var(--success-color)",
                            "medium": "var(--warning-color)",
                            "high": "var(--danger-color)"
                        }.get(severity, "gray")
                        
                        st.markdown(
                            f"""
                            <div class='pattern-card'>
                                <div class='pattern-header'>
                                    <span class='pattern-type'>{pattern.get('type', 'Unknown')}</span>
                                    <span class='pattern-severity' style='background-color:{severity_color};'>{severity.upper()}</span>
                                </div>
                                <p class='pattern-description'>{pattern.get('description', '')}</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        examples = pattern.get("examples", [])
                        if examples:
                            with st.expander("View Examples"):
                                for example in examples:
                                    st.markdown(f"- \"{example}\"")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Submit text in the Transform Content tab to see results here.")

# Tab 3: About
with tab3:
    st.markdown("### About Humanyze")
    
    st.markdown(
        """
        **Humanyze** is an AI Content Humanizer that transforms AI-generated text to sound more natural and human-like.
        
        #### Key Features:
        
        - **Pattern Analysis**: Detects common patterns in AI-generated text
        - **Style Transformation**: Adjusts content to match your preferred writing style
        - **Vocabulary Enhancement**: Replaces repetitive or formal language with more natural alternatives
        - **Structure Improvement**: Varies sentence structure and paragraph flow for a more human feel
        
        #### How to Use:
        
        1. Paste your AI-generated text in the input area
        2. Select your preferred writing style
        3. Choose processing mode (synchronous or asynchronous)
        4. Click "Humanize Text" to transform your content
        5. View the results and analysis in the Results tab
        
        #### Contact:
        
        For support or feedback, please contact us at support@humanyze.ai
        """
    )

# Footer
st.markdown(
    """
    <div class="footer">
        <p>© 2025 Humanyze. All rights reserved.</p>
    </div>
    """,
    unsafe_allow_html=True
)

def main():
    """Entry point for the Streamlit UI when installed as a package."""
    import streamlit.web.cli as stcli
    import sys
    import os
    
    sys.argv = [
        "streamlit", 
        "run", 
        __file__,
        "--server.port=" + os.getenv("UI_PORT", "8501"),
        "--server.address=" + os.getenv("UI_HOST", "0.0.0.0")
    ]
    
    stcli.main()

if __name__ == "__main__":
    main()
