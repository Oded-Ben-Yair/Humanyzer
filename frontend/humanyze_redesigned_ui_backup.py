
"""
Humanyze UI Redesign - Phase 1
This file implements the redesigned UI for Humanyze with improved layout, color scheme,
typography, and spacing while maintaining compatibility with the existing backend API.
"""
import streamlit as st
import json
import os
import sys
from pathlib import Path
import time
from datetime import datetime

# Import the UI utilities for API communication
# Adjust the import path as needed based on your project structure
sys.path.append('/home/ubuntu/humenizer')
from humenizer.ai_content_humanizer.ui.ui_utils import (
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

# Set page configuration
st.set_page_config(
    page_title="Humanyze - Make AI Sound Like You",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
import os

# Load redesigned styles
with open("/home/ubuntu/humanyze_redesigned_style.css") as f:
    redesigned_css = f.read()

# Load mobile responsive styles
mobile_css_path = os.path.join(os.path.dirname(__file__), "mobile.css")
if os.path.exists(mobile_css_path):
    with open(mobile_css_path) as f:
        mobile_css = f.read()
else:
    mobile_css = ""
        
# Combine and apply all styles
st.markdown(f"<style>{redesigned_css}\n{mobile_css}</style>", unsafe_allow_html=True)

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
if 'active_page' not in st.session_state:
    st.session_state.active_page = "Dashboard"
if 'usage_stats' not in st.session_state:
    # Placeholder for usage stats that would come from the backend in a real implementation
    st.session_state.usage_stats = {
        "transformations_today": 0,
        "transformations_total": 0,
        "last_transformation": None,
        "favorite_style": "professional"
    }

# Load profiles
def load_profiles():
    try:
        profiles_response = get_profiles()
        if profiles_response and "profiles" in profiles_response:
            st.session_state.profiles = profiles_response["profiles"]
    except Exception as e:
        st.error(f"Error loading profiles: {str(e)}")

# Load profiles on startup
if not st.session_state.profiles:
    load_profiles()

# Header with logo and navigation
st.markdown(
    """
    <div class="humanyze-header">
        <div class="logo-container">
            <h1>Humanyze</h1>
            <p class="tagline">Make AI Sound Like You</p>
        </div>
        <div class="trust-badge">
            <span class="badge">BETA</span>
        </div>
    </div>
    """, 
    unsafe_allow_html=True
)

# Main navigation
st.markdown('<div class="navigation-container">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Dashboard", use_container_width=True, 
                key="nav_dashboard", 
                type="secondary" if st.session_state.active_page != "Dashboard" else "primary"):
        st.session_state.active_page = "Dashboard"
        st.rerun()
with col2:
    if st.button("Transformation", use_container_width=True, 
                key="nav_transform", 
                type="secondary" if st.session_state.active_page != "Transformation" else "primary"):
        st.session_state.active_page = "Transformation"
        st.rerun()
with col3:
    if st.button("Results", use_container_width=True, 
                key="nav_results", 
                type="secondary" if st.session_state.active_page != "Results" else "primary"):
        st.session_state.active_page = "Results"
        st.rerun()
with col4:
    if st.button("Profiles", use_container_width=True, 
                key="nav_profiles", 
                type="secondary" if st.session_state.active_page != "Profiles" else "primary"):
        st.session_state.active_page = "Profiles"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Main content area
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Dashboard Page
if st.session_state.active_page == "Dashboard":
    st.markdown('<h2 class="page-title">Welcome to Humanyze</h2>', unsafe_allow_html=True)
    
    # User greeting with time-based message
    current_hour = datetime.now().hour
    greeting = "Good morning" if 5 <= current_hour < 12 else "Good afternoon" if 12 <= current_hour < 18 else "Good evening"
    
    st.markdown(f'<p class="welcome-message">{greeting}, User! Ready to transform your AI content?</p>', unsafe_allow_html=True)
    
    # Usage stats cards
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <h3>Today's Transformations</h3>
                <p class="stat-value">{st.session_state.usage_stats["transformations_today"]}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div class="stat-card">
                <h3>Total Transformations</h3>
                <p class="stat-value">{st.session_state.usage_stats["transformations_total"]}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            f"""
            <div class="stat-card">
                <h3>Favorite Style</h3>
                <p class="stat-value">{st.session_state.usage_stats["favorite_style"].capitalize()}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick actions
    st.markdown('<h3 class="section-title">Quick Actions</h3>', unsafe_allow_html=True)
    
    quick_action_col1, quick_action_col2 = st.columns(2)
    
    with quick_action_col1:
        if st.button("Start New Transformation", use_container_width=True, type="primary"):
            st.session_state.active_page = "Transformation"
            st.rerun()
    
    with quick_action_col2:
        if st.button("Manage Style Profiles", use_container_width=True):
            st.session_state.active_page = "Profiles"
            st.rerun()
    
    # Recent activity placeholder
    st.markdown('<h3 class="section-title">Recent Activity</h3>', unsafe_allow_html=True)
    
    if st.session_state.usage_stats["last_transformation"]:
        st.markdown(
            f"""
            <div class="recent-activity">
                <p>Last transformation: {st.session_state.usage_stats["last_transformation"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="recent-activity empty">
                <p>No recent activity. Start transforming your content!</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Onboarding placeholder
    with st.expander("New to Humanyze? Learn how it works"):
        st.markdown(
            """
            <div class="onboarding-content">
                <h4>How Humanyze Works</h4>
                <ol>
                    <li><strong>Input your text</strong> - Paste AI-generated content you want to transform</li>
                    <li><strong>Choose a style</strong> - Select from preset styles or create your own profile</li>
                    <li><strong>Transform</strong> - Our AI analyzes and transforms your content to sound more human</li>
                    <li><strong>Review results</strong> - Compare before and after, with detailed analysis</li>
                </ol>
                <p>Humanyze helps you maintain a consistent voice across all your AI-generated content.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Transformation Workspace Page
elif st.session_state.active_page == "Transformation":
    st.markdown('<h2 class="page-title">Transformation Workspace</h2>', unsafe_allow_html=True)
    
    # Context panel
    with st.expander("About Transformation", expanded=False):
        st.markdown(
            """
            The Transformation Workspace is where you can convert AI-generated text to sound more human.
            
            - Choose a style profile or use the basic styles
            - Paste your text and select processing options
            - Click "Transform" to humanize your content
            
            Your transformed text will appear in the Results page.
            """
        )
    
    # Main transformation area
    st.markdown('<div class="transformation-container">', unsafe_allow_html=True)
    
    # Style selection sidebar
    with st.sidebar:
        st.markdown('<h3 class="sidebar-title">Style Settings</h3>', unsafe_allow_html=True)
        
        # Profile selection
        st.markdown('<div class="profile-selector">', unsafe_allow_html=True)
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
        
        # Show selected profile details if any
        if st.session_state.selected_profile_id:
            for profile in st.session_state.profiles:
                if profile["id"] == st.session_state.selected_profile_id:
                    st.markdown(
                        f"""
                        <div class="profile-details">
                            <p><strong>Base Style:</strong> {profile.get("base_style", "casual").capitalize()}</p>
                            <p><strong>Tone:</strong> {profile.get("tone", "neutral").capitalize()}</p>
                            <p><strong>Formality:</strong> {profile.get("formality_level", 5)}/10</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Basic style options (when no profile is selected)
        if not st.session_state.selected_profile_id:
            st.markdown('<div class="basic-style-options">', unsafe_allow_html=True)
            style = st.selectbox(
                "Select writing style:",
                options=["casual", "professional", "creative"],
                index=0
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Use the profile's base style
            for profile in st.session_state.profiles:
                if profile["id"] == st.session_state.selected_profile_id:
                    style = profile.get("base_style", "casual")
        
        # Processing options
        st.markdown('<div class="processing-options">', unsafe_allow_html=True)
        st.markdown('<h4>Processing Options</h4>', unsafe_allow_html=True)
        
        process_mode = st.radio(
            "Processing mode:",
            options=["Synchronous", "Asynchronous"],
            index=0,
            horizontal=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Profile management shortcuts
        st.markdown('<div class="profile-actions">', unsafe_allow_html=True)
        st.markdown('<h4>Profile Management</h4>', unsafe_allow_html=True)
        
        profile_col1, profile_col2 = st.columns(2)
        
        with profile_col1:
            if st.button("Create New", use_container_width=True):
                st.session_state.active_page = "Profiles"
                st.session_state.show_profile_editor = True
                st.session_state.edit_profile_id = None
                st.rerun()
        
        with profile_col2:
            if st.session_state.selected_profile_id and st.button("Edit Current", use_container_width=True):
                st.session_state.active_page = "Profiles"
                st.session_state.show_profile_editor = True
                st.session_state.edit_profile_id = st.session_state.selected_profile_id
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Text input area
    st.markdown('<div class="text-input-container">', unsafe_allow_html=True)
    st.markdown('<h3>Input Text</h3>', unsafe_allow_html=True)
    
    text_input = st.text_area(
        "Paste your AI-generated text here:",
        height=300,
        key="text_input",
        value=st.session_state.original_text if st.session_state.original_text else "",
        placeholder="Enter or paste your AI-generated text here. The more text you provide, the better the transformation will be."
    )
    
    # Transform button
    if st.button("Transform Text", type="primary", use_container_width=True):
        if not text_input or not text_input.strip():
            st.error("Please enter some text to transform.")
        else:
            st.session_state.original_text = text_input
            
            with st.spinner("Transforming your text..."):
                if process_mode == "Synchronous":
                    # Synchronous processing
                    response = humanize_text(text_input, style, st.session_state.selected_profile_id)
                    
                    if response:
                        st.session_state.humanized_text = response.get("humanized", "")
                        st.session_state.analysis = response.get("analysis", None)
                        
                        # Update usage stats (placeholder for real implementation)
                        st.session_state.usage_stats["transformations_today"] += 1
                        st.session_state.usage_stats["transformations_total"] += 1
                        st.session_state.usage_stats["last_transformation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        st.success("Text transformed successfully!")
                        
                        # Switch to results page
                        st.session_state.active_page = "Results"
                        st.rerun()
                else:
                    # Asynchronous processing
                    response = humanize_text_async(text_input, style, st.session_state.selected_profile_id)
                    
                    if response:
                        st.session_state.job_id = response.get("job_id")
                        st.session_state.job_status = response.get("status")
                        st.info(f"Job submitted successfully! Job ID: {st.session_state.job_id}")
                        st.info("Check the Results page for status updates.")
                        
                        # Switch to results page
                        st.session_state.active_page = "Results"
                        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Results Experience Page
elif st.session_state.active_page == "Results":
    st.markdown('<h2 class="page-title">Results Experience</h2>', unsafe_allow_html=True)
    
    # Check if we have a job ID and it's still processing
    if st.session_state.job_id and st.session_state.job_status == "processing":
        st.markdown('<div class="job-status-container">', unsafe_allow_html=True)
        st.markdown(f'<h3>Job Status: <span class="processing-status">Processing</span></h3>', unsafe_allow_html=True)
        st.markdown(f'<p>Job ID: {st.session_state.job_id}</p>', unsafe_allow_html=True)
        
        if st.button("Check Job Status", type="primary"):
            with st.spinner("Checking job status..."):
                job_response = get_humanize_status(st.session_state.job_id)
                
                if job_response:
                    st.session_state.job_status = job_response.get("status")
                    
                    if job_response.get("status") == "completed":
                        result = job_response.get("result", {})
                        st.session_state.humanized_text = result.get("humanized", "")
                        st.session_state.analysis = result.get("analysis", None)
                        
                        # Update usage stats (placeholder for real implementation)
                        st.session_state.usage_stats["transformations_today"] += 1
                        st.session_state.usage_stats["transformations_total"] += 1
                        st.session_state.usage_stats["last_transformation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        st.success("Text transformation completed!")
                        st.rerun()
                    elif job_response.get("status") == "failed":
                        st.error(f"Job failed: {job_response.get('error', 'Unknown error')}")
                    else:
                        st.info(f"Job is still processing. Status: {job_response.get('status')}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display results if available
    if st.session_state.humanized_text:
        st.markdown('<div class="results-container">', unsafe_allow_html=True)
        
        # Before/After comparison
        st.markdown('<h3 class="comparison-title">Before & After Comparison</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="text-comparison original">', unsafe_allow_html=True)
            st.markdown('<h4>Original Text</h4>', unsafe_allow_html=True)
            st.text_area(
                "Original",
                value=st.session_state.original_text,
                height=300,
                disabled=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="text-comparison humanized">', unsafe_allow_html=True)
            st.markdown('<h4>Humanized Text</h4>', unsafe_allow_html=True)
            st.text_area(
                "Humanized",
                value=st.session_state.humanized_text,
                height=300,
                disabled=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Copy button for humanized text
        if st.button("Copy Humanized Text", use_container_width=True):
            st.code(st.session_state.humanized_text)
            st.success("Text copied to clipboard! (Use Ctrl+C to copy from the code block above)")
        
        # Analysis section
        if st.session_state.analysis:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown('<h3 class="analysis-title">Text Analysis</h3>', unsafe_allow_html=True)
            
            # AI likelihood
            is_likely_ai = st.session_state.analysis.get("is_likely_ai", False)
            ai_likelihood = "High" if is_likely_ai else "Low"
            likelihood_color = "var(--danger-color)" if is_likely_ai else "var(--success-color)"
            
            st.markdown(
                f"""
                <div class="ai-likelihood-container">
                    <h4>AI Detection Risk</h4>
                    <div class="likelihood-indicator">
                        <span class="likelihood-label">AI Likelihood:</span>
                        <span class="likelihood-value" style="color:{likelihood_color};">{ai_likelihood}</span>
                    </div>
                    <p class="likelihood-explanation">
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
            
            # Metrics
            metrics = st.session_state.analysis.get("metrics", {})
            if metrics:
                st.markdown('<div class="metrics-container">', unsafe_allow_html=True)
                st.markdown('<h4>Text Metrics</h4>', unsafe_allow_html=True)
                
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
            
            # Patterns found
            patterns = st.session_state.analysis.get("patterns_found", [])
            if patterns:
                st.markdown('<div class="patterns-container">', unsafe_allow_html=True)
                st.markdown('<h4>Detected Patterns</h4>', unsafe_allow_html=True)
                
                for pattern in patterns:
                    severity = pattern.get("severity", "low")
                    severity_color = {
                        "low": "var(--success-color)",
                        "medium": "var(--warning-color)",
                        "high": "var(--danger-color)"
                    }.get(severity, "var(--neutral-color)")
                    
                    st.markdown(
                        f"""
                        <div class="pattern-card">
                            <div class="pattern-header">
                                <span class="pattern-type">{pattern.get('type', 'Unknown')}</span>
                                <span class="pattern-severity" style="background-color:{severity_color};">{severity.upper()}</span>
                            </div>
                            <p class="pattern-description">{pattern.get('description', '')}</p>
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
        
        # Action buttons
        st.markdown('<div class="result-actions">', unsafe_allow_html=True)
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if st.button("Transform New Text", use_container_width=True, type="primary"):
                st.session_state.original_text = ""
                st.session_state.humanized_text = ""
                st.session_state.analysis = None
                st.session_state.job_id = None
                st.session_state.job_status = None
                st.session_state.active_page = "Transformation"
                st.rerun()
        
        with action_col2:
            if st.button("Edit & Retry", use_container_width=True):
                st.session_state.active_page = "Transformation"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # No results yet
        st.markdown(
            """
            <div class="no-results">
                <h3>No Results Yet</h3>
                <p>Transform text in the Transformation Workspace to see results here.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if st.button("Go to Transformation Workspace", type="primary"):
            st.session_state.active_page = "Transformation"
            st.rerun()

# Profile Management Page
elif st.session_state.active_page == "Profiles":
    st.markdown('<h2 class="page-title">Profile Management</h2>', unsafe_allow_html=True)
    
    # Profile editor
    if st.session_state.show_profile_editor:
        st.markdown('<div class="profile-editor-container">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <h3 class="editor-title">
                {
                    "Edit Profile" if st.session_state.edit_profile_id else "Create New Profile"
                }
            </h3>
            """, 
            unsafe_allow_html=True
        )
        
        # Initialize with existing profile data if editing
        profile_data = {}
        if st.session_state.edit_profile_id:
            for profile in st.session_state.profiles:
                if profile["id"] == st.session_state.edit_profile_id:
                    profile_data = profile
                    break
        
        # Profile form
        with st.form("profile_form"):
            st.markdown('<div class="form-section basic-info">', unsafe_allow_html=True)
            st.markdown('<h4>Basic Information</h4>', unsafe_allow_html=True)
            
            name = st.text_input(
                "Profile Name", 
                value=profile_data.get("name", ""),
                placeholder="Enter a descriptive name for this profile"
            )
            
            description = st.text_area(
                "Description", 
                value=profile_data.get("description", ""),
                placeholder="Describe the purpose and characteristics of this profile"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="form-section base-settings">', unsafe_allow_html=True)
            st.markdown('<h4>Base Settings</h4>', unsafe_allow_html=True)
            
            base_style = st.selectbox(
                "Base Style",
                options=["casual", "professional", "creative"],
                index=["casual", "professional", "creative"].index(profile_data.get("base_style", "casual"))
            )
            
            tone = st.text_input(
                "Tone", 
                value=profile_data.get("tone", "neutral"),
                placeholder="e.g., friendly, authoritative, enthusiastic"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="form-section style-params">', unsafe_allow_html=True)
            st.markdown('<h4>Style Parameters</h4>', unsafe_allow_html=True)
            
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
                    "Conversational Elements",
                    min_value=1,
                    max_value=10,
                    value=profile_data.get("conversational_element_frequency", 4),
                    help="1 = Few conversational elements, 10 = Many conversational elements"
                )
                
                sentence_variation_level = st.slider(
                    "Sentence Variation",
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
            
            st.markdown('<div class="form-section advanced-settings">', unsafe_allow_html=True)
            st.markdown('<h4>Advanced Settings</h4>', unsafe_allow_html=True)
            
            custom_phrases_text = "\n".join(profile_data.get("custom_phrases", []))
            custom_phrases = st.text_area(
                "Custom Phrases (one per line)",
                value=custom_phrases_text,
                help="Phrases to incorporate into the text",
                placeholder="Enter phrases that should be incorporated into the text"
            )
            
            avoid_phrases_text = "\n".join(profile_data.get("avoid_phrases", []))
            avoid_phrases = st.text_area(
                "Phrases to Avoid (one per line)",
                value=avoid_phrases_text,
                help="Phrases to avoid in the text",
                placeholder="Enter phrases that should be avoided in the text"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Submit buttons
            st.markdown('<div class="form-actions">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                submit = st.form_submit_button("Save Profile", use_container_width=True, type="primary")
            
            with col2:
                cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            with col3:
                if st.session_state.edit_profile_id:
                    delete = st.form_submit_button("Delete Profile", use_container_width=True)
                else:
                    delete = False
            
            st.markdown('</div>', unsafe_allow_html=True)
        
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
                    response = update_profile(st.session_state.edit_profile_id, profile_data)
                    if response:
                        st.success(f"Profile '{name}' updated successfully!")
                else:
                    # Create new profile
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
                st.error(f"Error saving profile: {str(e)}")
        
        if cancel:
            st.session_state.show_profile_editor = False
            st.session_state.edit_profile_id = None
            st.rerun()
        
        if delete and st.session_state.edit_profile_id:
            try:
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
                st.error(f"Error deleting profile: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Profile listing
        st.markdown('<div class="profiles-list-container">', unsafe_allow_html=True)
        
        # Create new profile button
        if st.button("Create New Profile", type="primary", key="create_new_profile_btn"):
            st.session_state.show_profile_editor = True
            st.session_state.edit_profile_id = None
            st.rerun()
        
        # Display existing profiles
        if st.session_state.profiles:
            st.markdown('<div class="profiles-grid">', unsafe_allow_html=True)
            
            # Create rows of profiles, 2 per row
            for i in range(0, len(st.session_state.profiles), 2):
                col1, col2 = st.columns(2)
                
                # First profile in the row
                with col1:
                    if i < len(st.session_state.profiles):
                        profile = st.session_state.profiles[i]
                        
                        st.markdown(
                            f"""
                            <div class="profile-card">
                                <h3 class="profile-name">{profile.get("name", "Unnamed Profile")}</h3>
                                <p class="profile-description">{profile.get("description", "No description")}</p>
                                <div class="profile-details">
                                    <p><strong>Base Style:</strong> {profile.get("base_style", "casual").capitalize()}</p>
                                    <p><strong>Tone:</strong> {profile.get("tone", "neutral").capitalize()}</p>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        profile_col1, profile_col2 = st.columns(2)
                        
                        with profile_col1:
                            if st.button("Edit", key=f"edit_{profile['id']}", use_container_width=True):
                                st.session_state.show_profile_editor = True
                                st.session_state.edit_profile_id = profile["id"]
                                st.rerun()
                        
                        with profile_col2:
                            if st.button("Use", key=f"use_{profile['id']}", use_container_width=True, type="primary"):
                                st.session_state.selected_profile_id = profile["id"]
                                st.session_state.active_page = "Transformation"
                                st.rerun()
                
                # Second profile in the row
                with col2:
                    if i + 1 < len(st.session_state.profiles):
                        profile = st.session_state.profiles[i + 1]
                        
                        st.markdown(
                            f"""
                            <div class="profile-card">
                                <h3 class="profile-name">{profile.get("name", "Unnamed Profile")}</h3>
                                <p class="profile-description">{profile.get("description", "No description")}</p>
                                <div class="profile-details">
                                    <p><strong>Base Style:</strong> {profile.get("base_style", "casual").capitalize()}</p>
                                    <p><strong>Tone:</strong> {profile.get("tone", "neutral").capitalize()}</p>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        profile_col1, profile_col2 = st.columns(2)
                        
                        with profile_col1:
                            if st.button("Edit", key=f"edit_{profile['id']}", use_container_width=True):
                                st.session_state.show_profile_editor = True
                                st.session_state.edit_profile_id = profile["id"]
                                st.rerun()
                        
                        with profile_col2:
                            if st.button("Use", key=f"use_{profile['id']}", use_container_width=True, type="primary"):
                                st.session_state.selected_profile_id = profile["id"]
                                st.session_state.active_page = "Transformation"
                                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                """
                <div class="no-profiles">
                    <h3>No Profiles Found</h3>
                    <p>Create your first style profile to get started.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)

# Trust elements placeholder (footer)
st.markdown(
    """
    <div class="trust-elements">
        <div class="trust-badge-container">
            <div class="trust-badge">
                <span>AI Ethics Compliant</span>
            </div>
            <div class="trust-badge">
                <span>Data Privacy Focused</span>
            </div>
            <div class="trust-badge">
                <span>Human-Centered Design</span>
            </div>
        </div>
        <p class="copyright">© 2025 Humanyze. All rights reserved.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)

# Main function for running the app
def main():
    """Entry point for the Streamlit UI when installed as a package."""
    # Get the directory of this script
    root_dir = Path(__file__).parent.parent.absolute()
    
    # Set the working directory to the project root
    os.chdir(root_dir)
    
    # Add the project root to the Python path
    sys.path.insert(0, str(root_dir))
    
    # Run the Streamlit app
    import streamlit.web.cli as stcli
    sys.argv = [
        "streamlit", 
        "run", 
        str(Path(__file__)),
        "--server.port=" + os.getenv("UI_PORT", "8501"),
        "--server.address=" + os.getenv("UI_HOST", "0.0.0.0")
    ]
    
    stcli.main()

if __name__ == "__main__":
    main()
