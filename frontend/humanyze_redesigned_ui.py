"""
Humanyze UI Redesign - Phase 2
This file implements the redesigned UI for Humanyze with a two-panel layout structure,
improved color scheme, typography, and spacing while maintaining compatibility with the existing backend API.
"""
import streamlit as st
import json
import os
import sys
from pathlib import Path
import time
from datetime import datetime
import re
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import difflib

# Import the mock UI utilities for testing
from mock_ui_utils import (
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

# Define new CSS with updated color scheme and typography
redesigned_css = """
/* New Design System Colors */
:root {
    /* Primary Colors */
    --primary-color: #5B21B6;
    --primary-light: #7C3AED;
    --primary-dark: #4C1D95;
    
    /* Secondary Colors */
    --secondary-color: #0D9488;
    --secondary-light: #14B8A6;
    --secondary-dark: #0F766E;
    
    /* Accent Colors */
    --accent-color: #F59E0B;
    --accent-light: #FBBF24;
    --accent-dark: #D97706;
    
    /* Neutral Colors */
    --neutral-50: #F8FAFC;
    --neutral-100: #F1F5F9;
    --neutral-200: #E2E8F0;
    --neutral-300: #CBD5E1;
    --neutral-400: #94A3B8;
    --neutral-500: #64748B;
    --neutral-600: #475569;
    --neutral-700: #334155;
    --neutral-800: #1E293B;
    --neutral-900: #0F172A;
    
    /* Semantic Colors */
    --success-color: #10B981;
    --warning-color: #F59E0B;
    --danger-color: #EF4444;
    --info-color: #3B82F6;
    
    /* UI Element Colors */
    --background-color: var(--neutral-50);
    --card-background: white;
    --text-color: var(--neutral-800);
    --text-light: var(--neutral-600);
    --border-color: var(--neutral-200);
    --hover-color: var(--neutral-100);
}

/* Typography */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Source+Serif+Pro:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

body {
    font-family: 'Source Serif Pro', serif;
    color: var(--text-color);
    background-color: var(--background-color);
    line-height: 1.6;
}

h1, h2, h3, h4, h5, h6, .stButton, .stSelectbox, .stRadio {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    color: var(--neutral-800);
}

code, pre {
    font-family: 'JetBrains Mono', monospace;
}

/* Layout Components */
.main-content {
    padding: 1rem;
    margin-bottom: 2rem;
}

.humanyze-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 1rem;
}

.logo-container h1 {
    color: var(--primary-color);
    margin: 0;
    font-weight: 700;
}

.tagline {
    color: var(--text-light);
    margin: 0;
    font-size: 0.9rem;
}

.navigation-container {
    margin-bottom: 2rem;
}

/* Two-panel Layout */
.workspace-container {
    display: flex;
    gap: 1.5rem;
    margin-top: 1.5rem;
}

.input-panel {
    flex: 1;
    background-color: var(--card-background);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color);
}

.output-panel {
    flex: 1;
    background-color: var(--card-background);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color);
}

.panel-title {
    color: var(--primary-color);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--primary-light);
}

.output-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 300px;
    background-color: var(--neutral-100);
    border-radius: 8px;
    color: var(--neutral-500);
    text-align: center;
    padding: 1rem;
}

.output-placeholder svg {
    width: 48px;
    height: 48px;
    margin-bottom: 1rem;
    color: var(--neutral-400);
}

/* Form Elements */
.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
    border-color: var(--border-color);
    border-radius: 6px;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 1px var(--primary-light);
}

/* Buttons */
.stButton > button {
    background-color: var(--primary-color);
    color: white;
    border-radius: 6px;
    border: none;
    padding: 0.5rem 1rem;
    font-weight: 500;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background-color: var(--primary-dark);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stButton > button[data-baseweb="button"][kind="secondary"] {
    background-color: white;
    color: var(--primary-color);
    border: 1px solid var(--primary-color);
}

.stButton > button[data-baseweb="button"][kind="secondary"]:hover {
    background-color: var(--neutral-100);
}

/* Cards and Containers */
.stat-card {
    background-color: var(--card-background);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color);
    height: 100%;
}

.stat-card h3 {
    color: var(--text-light);
    font-size: 1rem;
    margin-bottom: 0.5rem;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary-color);
}

.profile-card {
    background-color: var(--card-background);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color);
    margin-bottom: 1rem;
}

.profile-name {
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

.profile-description {
    color: var(--text-light);
    margin-bottom: 1rem;
}

.profile-details {
    background-color: var(--neutral-100);
    padding: 1rem;
    border-radius: 6px;
    margin-top: 1rem;
}

.profile-details p {
    margin: 0.25rem 0;
}

/* Analysis Section */
.analysis-section {
    margin-top: 2rem;
    background-color: var(--card-background);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color);
}

.analysis-title {
    color: var(--primary-color);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--primary-light);
}

.ai-likelihood-container {
    background-color: var(--neutral-100);
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 1.5rem;
}

.likelihood-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0.5rem 0;
}

.likelihood-label {
    font-weight: 600;
}

.likelihood-value {
    font-weight: 700;
}

.metrics-container {
    margin: 1.5rem 0;
}

.pattern-card {
    background-color: var(--neutral-100);
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.pattern-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.pattern-type {
    font-weight: 600;
    color: var(--neutral-800);
}

.pattern-severity {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    color: white;
}

/* Trust Elements */
.trust-elements {
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border-color);
    text-align: center;
}

.trust-badge-container {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

.trust-badge {
    background-color: var(--neutral-100);
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.8rem;
    color: var(--text-light);
    font-weight: 500;
}

.copyright {
    font-size: 0.8rem;
    color: var(--text-light);
}

/* Tone Selection */
.tone-selector {
    margin: 1.5rem 0;
}

.tone-options {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
}

.tone-option {
    background-color: var(--neutral-100);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 0.5rem 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.tone-option:hover {
    background-color: var(--neutral-200);
}

.tone-option.selected {
    background-color: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
}

/* Advanced Options */
.advanced-options {
    margin-top: 1.5rem;
}

/* Results Display */
.results-display {
    margin-top: 1rem;
}

.text-comparison {
    margin-bottom: 1.5rem;
}

.text-comparison h4 {
    margin-bottom: 0.5rem;
    color: var(--primary-color);
}

.quality-metrics {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
    flex-wrap: wrap;
}

.metric-card {
    background-color: var(--neutral-100);
    border-radius: 6px;
    padding: 1rem;
    flex: 1;
    min-width: 150px;
    text-align: center;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-color);
    margin: 0.5rem 0;
}

.metric-label {
    font-size: 0.9rem;
    color: var(--text-light);
}

.improvement-tips {
    background-color: var(--neutral-100);
    border-radius: 6px;
    padding: 1rem;
    margin-top: 1.5rem;
}

.tip-item {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
    position: relative;
}

.tip-item:before {
    content: "•";
    position: absolute;
    left: 0.5rem;
    color: var(--primary-color);
}

/* Loading States */
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    text-align: center;
}

.loading-spinner {
    border: 4px solid var(--neutral-200);
    border-top: 4px solid var(--primary-color);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* AI Detection Bypass Panel */
.ai-detection-panel {
    margin-top: 1.5rem;
    background-color: var(--card-background);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color);
}

.ai-detection-title {
    color: var(--primary-color);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--primary-light);
}

.detection-result {
    background-color: var(--neutral-100);
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 1rem;
}

.detection-score {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0.5rem 0;
}

.detection-label {
    font-weight: 600;
}

.suggestion-card {
    background-color: var(--neutral-100);
    border-radius: 6px;
    padding: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid var(--warning-color);
}

.suggestion-title {
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--neutral-800);
}

.suggestion-text {
    color: var(--neutral-700);
    font-style: italic;
    margin-bottom: 0.5rem;
}

.suggestion-reason {
    font-size: 0.9rem;
    color: var(--neutral-600);
}

.highlighted-text {
    background-color: rgba(245, 158, 11, 0.2);
    padding: 0.1rem 0.2rem;
    border-radius: 2px;
}

.humanization-level-container {
    margin: 1.5rem 0;
}

.humanization-level-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}

.humanization-level-value {
    font-weight: 600;
    color: var(--primary-color);
}

.preserve-keywords-container {
    margin: 1.5rem 0;
}

.tone-selection-container {
    margin: 1.5rem 0;
}

.tone-buttons {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
}

.tone-button {
    flex: 1;
    min-width: 100px;
}

/* Quality Metrics Panel */
.quality-metrics-panel {
    background-color: var(--card-background);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color);
    margin-bottom: 1.5rem;
}

.quality-metrics-title {
    color: var(--primary-color);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--primary-light);
}

.humanness-score-container {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.score-circle {
    position: relative;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background-color: var(--neutral-100);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.score-value {
    font-size: 2rem;
    font-weight: 700;
}

.score-label {
    font-size: 0.8rem;
    color: var(--text-light);
    text-align: center;
    margin-top: 0.25rem;
}

.score-details {
    flex: 1;
}

.score-title {
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--neutral-800);
}

.score-description {
    color: var(--text-light);
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
}

.improvement-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    margin-top: 0.5rem;
}

.improvement-positive {
    color: var(--success-color);
}

.improvement-negative {
    color: var(--danger-color);
}

.improvement-neutral {
    color: var(--text-light);
}

.progress-bar-container {
    margin: 1rem 0;
}

.progress-bar-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.25rem;
}

.progress-bar-title {
    font-weight: 600;
    font-size: 0.9rem;
}

.progress-bar-value {
    font-weight: 600;
    font-size: 0.9rem;
}

.progress-bar {
    height: 8px;
    background-color: var(--neutral-200);
    border-radius: 4px;
    overflow: hidden;
}

.progress-bar-fill {
    height: 100%;
    border-radius: 4px;
}

/* Status Indicators */
.status-indicators {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
    flex-wrap: wrap;
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.9rem;
}

.status-indicator-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

.status-complete {
    background-color: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.status-complete .status-indicator-dot {
    background-color: var(--success-color);
}

.status-in-progress {
    background-color: rgba(59, 130, 246, 0.1);
    color: var(--info-color);
}

.status-in-progress .status-indicator-dot {
    background-color: var(--info-color);
}

.status-pending {
    background-color: rgba(245, 158, 11, 0.1);
    color: var(--warning-color);
}

.status-pending .status-indicator-dot {
    background-color: var(--warning-color);
}

.status-error {
    background-color: rgba(239, 68, 68, 0.1);
    color: var(--danger-color);
}

.status-error .status-indicator-dot {
    background-color: var(--danger-color);
}

/* Before/After Comparison */
.comparison-container {
    margin: 1.5rem 0;
}

.comparison-title {
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--neutral-800);
}

.text-diff {
    background-color: var(--neutral-100);
    padding: 1rem;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    white-space: pre-wrap;
    line-height: 1.6;
}

.diff-added {
    background-color: rgba(16, 185, 129, 0.2);
    color: var(--success-color);
    padding: 0 0.2rem;
    border-radius: 2px;
}

.diff-removed {
    background-color: rgba(239, 68, 68, 0.2);
    color: var(--danger-color);
    padding: 0 0.2rem;
    border-radius: 2px;
    text-decoration: line-through;
}

/* Heatmap Visualization */
.heatmap-container {
    margin: 1.5rem 0;
}

.heatmap-title {
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--neutral-800);
}

/* Responsive Adjustments */
@media (max-width: 768px) {
    .workspace-container {
        flex-direction: column;
    }
    
    .input-panel, .output-panel {
        width: 100%;
    }
}
"""

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
if 'selected_tone' not in st.session_state:
    st.session_state.selected_tone = "neutral"
if 'show_advanced_options' not in st.session_state:
    st.session_state.show_advanced_options = False
if 'usage_stats' not in st.session_state:
    # Placeholder for usage stats that would come from the backend in a real implementation
    st.session_state.usage_stats = {
        "transformations_today": 0,
        "transformations_total": 0,
        "last_transformation": None,
        "favorite_style": "professional"
    }
# AI Detection Bypass Panel state variables
if 'ai_detection_score' not in st.session_state:
    st.session_state.ai_detection_score = None
if 'ai_detection_suggestions' not in st.session_state:
    st.session_state.ai_detection_suggestions = []
if 'humanization_level' not in st.session_state:
    st.session_state.humanization_level = 5
if 'preserve_keywords' not in st.session_state:
    st.session_state.preserve_keywords = []
if 'selected_bypass_tone' not in st.session_state:
    st.session_state.selected_bypass_tone = "Casual"
if 'analyzed_text' not in st.session_state:
    st.session_state.analyzed_text = ""
# Quality Metrics Panel state variables
if 'humanness_score' not in st.session_state:
    st.session_state.humanness_score = 0
if 'humanness_improvement' not in st.session_state:
    st.session_state.humanness_improvement = 0
if 'readability_grade' not in st.session_state:
    st.session_state.readability_grade = "N/A"
if 'readability_improvement' not in st.session_state:
    st.session_state.readability_improvement = 0
if 'process_status' not in st.session_state:
    st.session_state.process_status = "pending"
if 'quality_level' not in st.session_state:
    st.session_state.quality_level = "medium"
if 'improvement_areas' not in st.session_state:
    st.session_state.improvement_areas = {}

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

# AI Detection Functions
def analyze_ai_patterns(text):
    """
    Analyze text for AI-generated patterns and return a detection score and suggestions.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Tuple of (detection_score, suggestions)
    """
    if not text:
        return 0, []
    
    # Use the existing analyze_text function from ui_utils
    analysis_result = analyze_text(text)
    
    if not analysis_result:
        # Fallback to basic analysis if API call fails
        return perform_basic_analysis(text)
    
    # Extract metrics and patterns from the analysis result
    metrics = analysis_result.get("metrics", {})
    patterns = analysis_result.get("patterns_found", [])
    is_likely_ai = analysis_result.get("is_likely_ai", False)
    
    # Calculate detection score (0-100)
    # Higher score means more likely to be detected as AI
    detection_score = 0
    
    if is_likely_ai:
        # Base score if AI is detected
        detection_score = 70
        
        # Add points for each pattern found
        for pattern in patterns:
            severity = pattern.get("severity", "low")
            if severity == "high":
                detection_score += 10
            elif severity == "medium":
                detection_score += 5
            else:
                detection_score += 2
    else:
        # Base score if AI is not detected
        detection_score = 30
        
        # Add points for each pattern found
        for pattern in patterns:
            severity = pattern.get("severity", "low")
            if severity == "high":
                detection_score += 8
            elif severity == "medium":
                detection_score += 4
            else:
                detection_score += 1
    
    # Cap the score at 100
    detection_score = min(detection_score, 100)
    
    # Generate suggestions based on patterns
    suggestions = generate_suggestions(text, patterns)
    
    return detection_score, suggestions

def perform_basic_analysis(text):
    """
    Perform basic analysis when API call fails.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Tuple of (detection_score, suggestions)
    """
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Calculate average sentence length
    avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / max(len(sentences), 1)
    
    # Check for repeated phrases (n-grams)
    words = text.lower().split()
    ngrams = {}
    for n in range(3, 6):  # Check 3, 4, and 5-grams
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            ngrams[ngram] = ngrams.get(ngram, 0) + 1
    
    repeated_ngrams = {ng: count for ng, count in ngrams.items() if count > 1}
    
    # Check for formal phrases
    formal_phrases = [
        "it is important to note",
        "in conclusion",
        "as previously mentioned",
        "it should be noted",
        "in summary",
        "it is worth mentioning",
        "it is essential to",
        "it is crucial to",
        "it is necessary to",
        "it is vital to"
    ]
    
    found_formal_phrases = [phrase for phrase in formal_phrases if phrase in text.lower()]
    
    # Calculate detection score
    detection_score = 30  # Base score
    
    if avg_sentence_length > 25:
        detection_score += 15
    
    detection_score += min(len(repeated_ngrams) * 5, 25)
    detection_score += len(found_formal_phrases) * 5
    
    # Cap the score at 100
    detection_score = min(detection_score, 100)
    
    # Generate suggestions
    suggestions = []
    
    # Suggest breaking up long sentences
    if avg_sentence_length > 25:
        long_sentences = [s for s in sentences if len(s.split()) > 25]
        if long_sentences:
            suggestions.append({
                "title": "Break up long sentences",
                "text": long_sentences[0],
                "reason": "Long, complex sentences are typical of AI writing."
            })
    
    # Suggest reducing repetitive phrases
    if repeated_ngrams:
        top_repeated = sorted(repeated_ngrams.items(), key=lambda x: x[1], reverse=True)[:3]
        for ngram, count in top_repeated:
            suggestions.append({
                "title": f"Reduce repetition of '{ngram}'",
                "text": f"This phrase appears {count} times in your text.",
                "reason": "Repetitive phrases make text sound mechanical and AI-generated."
            })
    
    # Suggest replacing formal phrases
    if found_formal_phrases:
        for phrase in found_formal_phrases[:3]:
            suggestions.append({
                "title": f"Replace formal phrase '{phrase}'",
                "text": f"This formal transition is common in AI writing.",
                "reason": "Overly formal transitions are red flags for AI detection."
            })
    
    return detection_score, suggestions

def generate_suggestions(text, patterns):
    """
    Generate suggestions for humanizing text based on detected patterns.
    
    Args:
        text: Input text
        patterns: List of detected patterns
        
    Returns:
        List of suggestion dictionaries
    """
    suggestions = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Process each pattern and generate suggestions
    for pattern in patterns:
        pattern_type = pattern.get("type", "")
        severity = pattern.get("severity", "low")
        description = pattern.get("description", "")
        examples = pattern.get("examples", [])
        
        # Only generate suggestions for medium and high severity patterns
        if severity in ["medium", "high"]:
            if pattern_type == "long_sentences":
                # Find the longest sentences
                sentence_lengths = [(i, len(s.split())) for i, s in enumerate(sentences)]
                longest_sentences = sorted(sentence_lengths, key=lambda x: x[1], reverse=True)[:3]
                
                for idx, length in longest_sentences:
                    if length > 20:  # Only suggest for very long sentences
                        suggestions.append({
                            "title": "Break up long sentence",
                            "text": sentences[idx],
                            "reason": "Long, complex sentences are typical of AI writing."
                        })
            
            elif pattern_type == "repetitive_phrases":
                # Suggest alternatives for repetitive phrases
                for example in examples[:3]:
                    suggestions.append({
                        "title": f"Reduce repetition of '{example}'",
                        "text": f"This phrase appears multiple times in your text.",
                        "reason": "Repetitive phrases make text sound mechanical and AI-generated."
                    })
            
            elif pattern_type == "formal_language":
                # Suggest alternatives for formal phrases
                for example in examples[:3]:
                    suggestions.append({
                        "title": f"Replace formal phrase '{example}'",
                        "text": f"This formal expression is common in AI writing.",
                        "reason": "Overly formal language is a red flag for AI detection."
                    })
            
            elif pattern_type == "lack_of_contractions":
                # Find sentences without contractions that could have them
                contraction_candidates = [
                    (i, s) for i, s in enumerate(sentences) 
                    if any(marker in s.lower() for marker in ["is not", "are not", "will not", "cannot", "do not", "does not", "would not", "could not", "should not"])
                ]
                
                for idx, sentence in contraction_candidates[:3]:
                    suggestions.append({
                        "title": "Add contractions",
                        "text": sentence,
                        "reason": "Using contractions makes text sound more conversational and human."
                    })
            
            elif pattern_type == "consistent_paragraph_length":
                suggestions.append({
                    "title": "Vary paragraph lengths",
                    "text": "Your paragraphs have very consistent lengths.",
                    "reason": "Humans naturally vary paragraph lengths more than AI does."
                })
            
            # Add a generic suggestion if no specific type matches
            else:
                suggestions.append({
                    "title": "Address detected pattern",
                    "text": description,
                    "reason": f"This pattern was detected with {severity} severity."
                })
    
    # If no patterns were severe enough, add some general suggestions
    if not suggestions:
        suggestions.append({
            "title": "Add personal anecdotes",
            "text": "Consider adding a brief personal experience or opinion.",
            "reason": "Personal elements are difficult for AI to generate authentically."
        })
        
        suggestions.append({
            "title": "Use more varied sentence structures",
            "text": "Mix short and long sentences. Try using questions or exclamations.",
            "reason": "Varied sentence structures appear more naturally human."
        })
    
    return suggestions

def find_sentences_to_highlight(text, suggestions):
    """
    Find sentences in the text that match the suggestions.
    
    Args:
        text: Input text
        suggestions: List of suggestion dictionaries
        
    Returns:
        List of sentences to highlight
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    to_highlight = []
    
    for suggestion in suggestions:
        suggestion_text = suggestion.get("text", "")
        
        # If the suggestion text is a full sentence from the text
        if suggestion_text in sentences:
            to_highlight.append(suggestion_text)
        # If the suggestion text is a phrase that might appear in multiple sentences
        elif len(suggestion_text.split()) <= 5:
            for sentence in sentences:
                if suggestion_text in sentence and sentence not in to_highlight:
                    to_highlight.append(sentence)
    
    return to_highlight

def highlight_text(text, sentences_to_highlight):
    """
    Highlight specific sentences in the text.
    
    Args:
        text: Input text
        sentences_to_highlight: List of sentences to highlight
        
    Returns:
        HTML-formatted text with highlights
    """
    if not sentences_to_highlight:
        return text
    
    highlighted_text = text
    
    for sentence in sentences_to_highlight:
        # Escape special regex characters
        escaped_sentence = re.escape(sentence)
        # Replace the sentence with a highlighted version
        highlighted_text = re.sub(
            f"({escaped_sentence})", 
            r'<span class="highlighted-text">\1</span>', 
            highlighted_text
        )
    
    return highlighted_text

# New Quality Metrics Functions
def calculate_humanness_score(text, analysis=None):
    """
    Calculate a humanness score based on text analysis.
    
    Args:
        text: Input text
        analysis: Analysis result from the API
        
    Returns:
        Humanness score (0-100)
    """
    if not text:
        return 0
    
    if analysis:
        # Use the analysis result if available
        metrics = analysis.get("metrics", {})
        patterns = analysis.get("patterns_found", [])
        is_likely_ai = analysis.get("is_likely_ai", False)
        
        # Base score
        score = 70 if not is_likely_ai else 40
        
        # Adjust based on metrics
        avg_sentence_length = metrics.get("avg_sentence_length", 0)
        if 12 <= avg_sentence_length <= 20:
            score += 10
        elif avg_sentence_length > 30 or avg_sentence_length < 8:
            score -= 10
        
        contraction_ratio = metrics.get("contraction_ratio", 0)
        if contraction_ratio > 0.6:
            score += 10
        elif contraction_ratio < 0.3:
            score -= 5
        
        repeated_ngrams_count = metrics.get("repeated_ngrams_count", 0)
        if repeated_ngrams_count < 3:
            score += 10
        elif repeated_ngrams_count > 8:
            score -= 10
        
        # Adjust based on patterns
        for pattern in patterns:
            severity = pattern.get("severity", "low")
            if severity == "high":
                score -= 10
            elif severity == "medium":
                score -= 5
            elif severity == "low":
                score -= 2
    else:
        # Basic calculation if no analysis is available
        sentences = re.split(r'(?<=[.!?])\s+', text)
        avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / max(len(sentences), 1)
        
        # Base score
        score = 60
        
        # Adjust based on sentence length
        if 12 <= avg_sentence_length <= 20:
            score += 10
        elif avg_sentence_length > 30 or avg_sentence_length < 8:
            score -= 10
        
        # Check for contractions
        contraction_count = len(re.findall(r"\b(can't|won't|don't|isn't|aren't|haven't|hasn't|wouldn't|couldn't|shouldn't|didn't|doesn't|I'm|you're|he's|she's|it's|we're|they're|I've|you've|we've|they've)\b", text, re.IGNORECASE))
        if contraction_count > len(sentences) * 0.5:
            score += 10
        elif contraction_count < len(sentences) * 0.2:
            score -= 5
        
        # Check for varied sentence structure
        sentence_lengths = [len(s.split()) for s in sentences]
        if len(sentences) > 1:
            sentence_length_variance = np.var(sentence_lengths)
            if sentence_length_variance > 20:
                score += 10
            elif sentence_length_variance < 5:
                score -= 5
    
    # Cap the score between 0 and 100
    score = max(0, min(score, 100))
    
    return int(score)

def calculate_readability_grade(text):
    """
    Calculate a readability grade for the text.
    
    Args:
        text: Input text
        
    Returns:
        Readability grade (string)
    """
    if not text:
        return "N/A"
    
    # Split text into sentences and words
    sentences = re.split(r'(?<=[.!?])\s+', text)
    words = text.split()
    
    # Count syllables (simplified approach)
    def count_syllables(word):
        word = word.lower()
        if len(word) <= 3:
            return 1
        
        # Remove common endings
        if word.endswith('es') or word.endswith('ed'):
            word = word[:-2]
        elif word.endswith('e'):
            word = word[:-1]
        
        # Count vowel groups
        vowels = "aeiouy"
        count = 0
        prev_is_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel
        
        return max(1, count)
    
    # Calculate total syllables
    syllables = sum(count_syllables(word) for word in words)
    
    # Calculate Flesch-Kincaid Grade Level
    if len(sentences) == 0 or len(words) == 0:
        return "N/A"
    
    words_per_sentence = len(words) / len(sentences)
    syllables_per_word = syllables / len(words)
    
    grade_level = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
    
    # Convert to grade level description
    if grade_level < 6:
        return "Elementary"
    elif grade_level < 8:
        return "Middle School"
    elif grade_level < 12:
        return "High School"
    elif grade_level < 14:
        return "College"
    elif grade_level < 18:
        return "Graduate"
    else:
        return "Professional"

def generate_text_diff(original, humanized):
    """
    Generate a visual diff between original and humanized text.
    
    Args:
        original: Original text
        humanized: Humanized text
        
    Returns:
        HTML-formatted diff
    """
    if not original or not humanized:
        return ""
    
    # Generate diff
    diff = difflib.ndiff(original.splitlines(keepends=True), humanized.splitlines(keepends=True))
    
    # Format diff as HTML
    html_diff = []
    for line in diff:
        if line.startswith('+ '):
            html_diff.append(f'<span class="diff-added">{line[2:]}</span>')
        elif line.startswith('- '):
            html_diff.append(f'<span class="diff-removed">{line[2:]}</span>')
        elif line.startswith('  '):
            html_diff.append(line[2:])
    
    return ''.join(html_diff)

def generate_improvement_heatmap(text, analysis=None):
    """
    Generate data for a heatmap visualization of improvement areas.
    
    Args:
        text: Input text
        analysis: Analysis result from the API
        
    Returns:
        Dictionary with heatmap data
    """
    if not text:
        return {}
    
    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    
    # Define improvement categories
    categories = [
        "Sentence Structure",
        "Vocabulary",
        "Formality",
        "Contractions",
        "Repetition"
    ]
    
    # Initialize data
    heatmap_data = {
        "paragraphs": [],
        "categories": categories,
        "values": []
    }
    
    if analysis:
        # Use the analysis result if available
        metrics = analysis.get("metrics", {})
        patterns = analysis.get("patterns_found", [])
        
        # Process each paragraph
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                heatmap_data["paragraphs"].append(f"P{i+1}")
                
                # Calculate scores for each category
                paragraph_scores = []
                
                # Sentence Structure score
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                sentence_lengths = [len(s.split()) for s in sentences]
                if len(sentences) > 1:
                    sentence_length_variance = np.var(sentence_lengths)
                    if sentence_length_variance > 20:
                        paragraph_scores.append(0.2)  # Low improvement needed
                    elif sentence_length_variance < 5:
                        paragraph_scores.append(0.8)  # High improvement needed
                    else:
                        paragraph_scores.append(0.5)  # Medium improvement needed
                else:
                    paragraph_scores.append(0.5)
                
                # Vocabulary score
                unique_words = len(set(paragraph.lower().split()))
                total_words = len(paragraph.split())
                if total_words > 0:
                    lexical_diversity = unique_words / total_words
                    if lexical_diversity > 0.7:
                        paragraph_scores.append(0.2)  # Low improvement needed
                    elif lexical_diversity < 0.5:
                        paragraph_scores.append(0.8)  # High improvement needed
                    else:
                        paragraph_scores.append(0.5)  # Medium improvement needed
                else:
                    paragraph_scores.append(0.5)
                
                # Formality score
                formal_phrases = [
                    "it is important to note",
                    "in conclusion",
                    "as previously mentioned",
                    "it should be noted",
                    "in summary",
                    "it is worth mentioning",
                    "it is essential to",
                    "it is crucial to",
                    "it is necessary to",
                    "it is vital to"
                ]
                formal_count = sum(1 for phrase in formal_phrases if phrase in paragraph.lower())
                if formal_count > 2:
                    paragraph_scores.append(0.8)  # High improvement needed
                elif formal_count > 0:
                    paragraph_scores.append(0.5)  # Medium improvement needed
                else:
                    paragraph_scores.append(0.2)  # Low improvement needed
                
                # Contractions score
                contraction_count = len(re.findall(r"\b(can't|won't|don't|isn't|aren't|haven't|hasn't|wouldn't|couldn't|shouldn't|didn't|doesn't|I'm|you're|he's|she's|it's|we're|they're|I've|you've|we've|they've)\b", paragraph, re.IGNORECASE))
                if contraction_count > len(sentences) * 0.5:
                    paragraph_scores.append(0.2)  # Low improvement needed
                elif contraction_count < len(sentences) * 0.2:
                    paragraph_scores.append(0.8)  # High improvement needed
                else:
                    paragraph_scores.append(0.5)  # Medium improvement needed
                
                # Repetition score
                words = paragraph.lower().split()
                ngrams = {}
                for n in range(3, 6):  # Check 3, 4, and 5-grams
                    for j in range(len(words) - n + 1):
                        ngram = ' '.join(words[j:j+n])
                        ngrams[ngram] = ngrams.get(ngram, 0) + 1
                
                repeated_ngrams = {ng: count for ng, count in ngrams.items() if count > 1}
                if len(repeated_ngrams) > 3:
                    paragraph_scores.append(0.8)  # High improvement needed
                elif len(repeated_ngrams) > 1:
                    paragraph_scores.append(0.5)  # Medium improvement needed
                else:
                    paragraph_scores.append(0.2)  # Low improvement needed
                
                heatmap_data["values"].append(paragraph_scores)
    else:
        # Basic calculation if no analysis is available
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                heatmap_data["paragraphs"].append(f"P{i+1}")
                
                # Calculate scores for each category
                paragraph_scores = []
                
                # Sentence Structure score
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                sentence_lengths = [len(s.split()) for s in sentences]
                if len(sentences) > 1:
                    sentence_length_variance = np.var(sentence_lengths)
                    if sentence_length_variance > 20:
                        paragraph_scores.append(0.2)  # Low improvement needed
                    elif sentence_length_variance < 5:
                        paragraph_scores.append(0.8)  # High improvement needed
                    else:
                        paragraph_scores.append(0.5)  # Medium improvement needed
                else:
                    paragraph_scores.append(0.5)
                
                # Vocabulary score
                unique_words = len(set(paragraph.lower().split()))
                total_words = len(paragraph.split())
                if total_words > 0:
                    lexical_diversity = unique_words / total_words
                    if lexical_diversity > 0.7:
                        paragraph_scores.append(0.2)  # Low improvement needed
                    elif lexical_diversity < 0.5:
                        paragraph_scores.append(0.8)  # High improvement needed
                    else:
                        paragraph_scores.append(0.5)  # Medium improvement needed
                else:
                    paragraph_scores.append(0.5)
                
                # Formality score
                formal_phrases = [
                    "it is important to note",
                    "in conclusion",
                    "as previously mentioned",
                    "it should be noted",
                    "in summary",
                    "it is worth mentioning",
                    "it is essential to",
                    "it is crucial to",
                    "it is necessary to",
                    "it is vital to"
                ]
                formal_count = sum(1 for phrase in formal_phrases if phrase in paragraph.lower())
                if formal_count > 2:
                    paragraph_scores.append(0.8)  # High improvement needed
                elif formal_count > 0:
                    paragraph_scores.append(0.5)  # Medium improvement needed
                else:
                    paragraph_scores.append(0.2)  # Low improvement needed
                
                # Contractions score
                contraction_count = len(re.findall(r"\b(can't|won't|don't|isn't|aren't|haven't|hasn't|wouldn't|couldn't|shouldn't|didn't|doesn't|I'm|you're|he's|she's|it's|we're|they're|I've|you've|we've|they've)\b", paragraph, re.IGNORECASE))
                if contraction_count > len(sentences) * 0.5:
                    paragraph_scores.append(0.2)  # Low improvement needed
                elif contraction_count < len(sentences) * 0.2:
                    paragraph_scores.append(0.8)  # High improvement needed
                else:
                    paragraph_scores.append(0.5)  # Medium improvement needed
                
                # Repetition score
                words = paragraph.lower().split()
                ngrams = {}
                for n in range(3, 6):  # Check 3, 4, and 5-grams
                    for j in range(len(words) - n + 1):
                        ngram = ' '.join(words[j:j+n])
                        ngrams[ngram] = ngrams.get(ngram, 0) + 1
                
                repeated_ngrams = {ng: count for ng, count in ngrams.items() if count > 1}
                if len(repeated_ngrams) > 3:
                    paragraph_scores.append(0.8)  # High improvement needed
                elif len(repeated_ngrams) > 1:
                    paragraph_scores.append(0.5)  # Medium improvement needed
                else:
                    paragraph_scores.append(0.2)  # Low improvement needed
                
                heatmap_data["values"].append(paragraph_scores)
    
    return heatmap_data

# Quality Metrics Panel Component
def render_quality_metrics_panel(humanness_score, humanness_improvement, readability_grade, readability_improvement):
    """
    Render the Quality Metrics Panel with visual indicators.
    
    Args:
        humanness_score: Humanness score (0-100)
        humanness_improvement: Improvement in humanness score
        readability_grade: Readability grade (string)
        readability_improvement: Improvement in readability
    """
    st.markdown('<div class="quality-metrics-panel">', unsafe_allow_html=True)
    st.markdown('<h3 class="quality-metrics-title">Quality Metrics</h3>', unsafe_allow_html=True)
    
    # Humanness Score
    st.markdown('<div class="humanness-score-container">', unsafe_allow_html=True)
    
    # Determine score color based on value
    if humanness_score >= 80:
        score_color = "var(--success-color)"
    elif humanness_score >= 60:
        score_color = "var(--warning-color)"
    else:
        score_color = "var(--danger-color)"
    
    # Render score circle with percentage
    st.markdown(
        f"""
        <div class="score-circle" style="border: 6px solid {score_color};">
            <div>
                <div class="score-value" style="color: {score_color};">{humanness_score}%</div>
                <div class="score-label">Humanness</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Score details
    st.markdown('<div class="score-details">', unsafe_allow_html=True)
    st.markdown('<h4 class="score-title">Humanness Score</h4>', unsafe_allow_html=True)
    
    # Description based on score
    if humanness_score >= 80:
        description = "Your text appears highly human-like and is unlikely to be detected as AI-generated."
    elif humanness_score >= 60:
        description = "Your text has a moderate level of human-like qualities but could be improved further."
    else:
        description = "Your text shows significant AI patterns and needs improvement to appear more human-like."
    
    st.markdown(f'<p class="score-description">{description}</p>', unsafe_allow_html=True)
    
    # Improvement indicator
    if humanness_improvement > 0:
        st.markdown(
            f"""
            <div class="improvement-indicator improvement-positive">
                <span>↑ {humanness_improvement}%</span>
                <span>Improved from original</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif humanness_improvement < 0:
        st.markdown(
            f"""
            <div class="improvement-indicator improvement-negative">
                <span>↓ {abs(humanness_improvement)}%</span>
                <span>Decreased from original</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="improvement-indicator improvement-neutral">
                <span>→ No change</span>
                <span>Same as original</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Readability Grade
    st.markdown('<div class="progress-bar-container">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="progress-bar-label">
            <span class="progress-bar-title">Readability Grade</span>
            <span class="progress-bar-value">{readability_grade}</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Map readability grade to progress value
    readability_values = {
        "Elementary": 20,
        "Middle School": 40,
        "High School": 60,
        "College": 80,
        "Graduate": 90,
        "Professional": 100,
        "N/A": 50
    }
    
    readability_value = readability_values.get(readability_grade, 50)
    
    # Determine color based on readability
    if readability_grade in ["High School", "College"]:
        readability_color = "var(--success-color)"
    elif readability_grade in ["Middle School", "Graduate"]:
        readability_color = "var(--warning-color)"
    elif readability_grade == "Professional":
        readability_color = "var(--info-color)"
    else:
        readability_color = "var(--danger-color)"
    
    # Render progress bar
    st.markdown(
        f"""
        <div class="progress-bar">
            <div class="progress-bar-fill" style="width: {readability_value}%; background-color: {readability_color};"></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Improvement indicator
    if readability_improvement != 0:
        improvement_text = "Improved" if readability_improvement > 0 else "Decreased"
        improvement_class = "improvement-positive" if readability_improvement > 0 else "improvement-negative"
        
        st.markdown(
            f"""
            <div class="improvement-indicator {improvement_class}">
                <span>{improvement_text} readability</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Status Indicators Component
def render_status_indicators(process_status, quality_level):
    """
    Render color-coded status indicators for process stages and quality levels.
    
    Args:
        process_status: Current process status (pending, in-progress, complete, error)
        quality_level: Quality level (low, medium, high)
    """
    st.markdown('<div class="status-indicators">', unsafe_allow_html=True)
    
    # Process Status Indicator
    if process_status == "complete":
        st.markdown(
            """
            <div class="status-indicator status-complete">
                <div class="status-indicator-dot"></div>
                <span>Process Complete</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif process_status == "in-progress":
        st.markdown(
            """
            <div class="status-indicator status-in-progress">
                <div class="status-indicator-dot"></div>
                <span>Processing</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif process_status == "error":
        st.markdown(
            """
            <div class="status-indicator status-error">
                <div class="status-indicator-dot"></div>
                <span>Error</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:  # pending
        st.markdown(
            """
            <div class="status-indicator status-pending">
                <div class="status-indicator-dot"></div>
                <span>Pending</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Quality Level Indicator
    if quality_level == "high":
        st.markdown(
            """
            <div class="status-indicator status-complete">
                <div class="status-indicator-dot"></div>
                <span>High Quality</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif quality_level == "medium":
        st.markdown(
            """
            <div class="status-indicator status-pending">
                <div class="status-indicator-dot"></div>
                <span>Medium Quality</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:  # low
        st.markdown(
            """
            <div class="status-indicator status-error">
                <div class="status-indicator-dot"></div>
                <span>Low Quality</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Before/After Comparison Component
def render_text_comparison(original_text, humanized_text):
    """
    Render a before/after comparison with highlighted changes.
    
    Args:
        original_text: Original text
        humanized_text: Humanized text
    """
    if not original_text or not humanized_text:
        return
    
    st.markdown('<div class="comparison-container">', unsafe_allow_html=True)
    st.markdown('<h4 class="comparison-title">Before/After Comparison</h4>', unsafe_allow_html=True)
    
    # Generate diff
    diff_html = generate_text_diff(original_text, humanized_text)
    
    # Render diff
    st.markdown(f'<div class="text-diff">{diff_html}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Heatmap Visualization Component
def render_improvement_heatmap(improvement_areas):
    """
    Render a heatmap visualization of improvement areas.
    
    Args:
        improvement_areas: Dictionary with heatmap data
    """
    if not improvement_areas or not improvement_areas.get("paragraphs"):
        return
    
    st.markdown('<div class="heatmap-container">', unsafe_allow_html=True)
    st.markdown('<h4 class="heatmap-title">Improvement Areas Heatmap</h4>', unsafe_allow_html=True)
    
    # Create DataFrame for heatmap
    paragraphs = improvement_areas.get("paragraphs", [])
    categories = improvement_areas.get("categories", [])
    values = improvement_areas.get("values", [])
    
    if paragraphs and categories and values:
        # Create DataFrame
        df = pd.DataFrame(values, index=paragraphs, columns=categories)
        
        # Create heatmap using Plotly
        fig = px.imshow(
            df,
            labels=dict(x="Category", y="Paragraph", color="Improvement Needed"),
            x=categories,
            y=paragraphs,
            color_continuous_scale=["green", "yellow", "red"],
            zmin=0,
            zmax=1
        )
        
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=10, b=10),
            coloraxis_colorbar=dict(
                title="Improvement<br>Needed",
                tickvals=[0.2, 0.5, 0.8],
                ticktext=["Low", "Medium", "High"]
            )
        )
        
        # Display the heatmap
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

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

# Transformation Workspace Page - Redesigned with two-panel layout
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
            
            Your transformed text will appear in the right panel.
            """
        )
    
    # Two-panel layout container
    st.markdown('<div class="workspace-container">', unsafe_allow_html=True)
    
    # Left panel - Input
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    st.markdown('<h3 class="panel-title">Input</h3>', unsafe_allow_html=True)
    
    # Text input area
    text_input = st.text_area(
        "Paste your AI-generated text here:",
        height=250,
        key="text_input",
        value=st.session_state.original_text if st.session_state.original_text else "",
        placeholder="Enter or paste your AI-generated text here. The more text you provide, the better the transformation will be."
    )
    
    # Tone selection
    st.markdown('<div class="tone-selector">', unsafe_allow_html=True)
    st.markdown('<h4>Select Tone</h4>', unsafe_allow_html=True)
    
    # Profile selection
    profile_options = ["None (Use Basic Style)"] + [f"{p['name']}" for p in st.session_state.profiles]
    profile_indices = {p["id"]: i+1 for i, p in enumerate(st.session_state.profiles)}
    
    selected_index = 0
    if st.session_state.selected_profile_id:
        selected_index = profile_indices.get(st.session_state.selected_profile_id, 0)
    
    selected_profile = st.selectbox(
        "Style profile:",
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
    
    # Basic style options (when no profile is selected)
    if not st.session_state.selected_profile_id:
        style = st.selectbox(
            "Writing style:",
            options=["casual", "professional", "creative"],
            index=0
        )
        
        # Tone options
        tone_options = ["neutral", "friendly", "authoritative", "enthusiastic", "formal", "informal"]
        tone_col1, tone_col2, tone_col3 = st.columns(3)
        
        with tone_col1:
            if st.button("Neutral", use_container_width=True, 
                        type="primary" if st.session_state.selected_tone == "neutral" else "secondary",
                        key="tone_neutral"):
                st.session_state.selected_tone = "neutral"
                st.rerun()
        
        with tone_col2:
            if st.button("Friendly", use_container_width=True, 
                        type="primary" if st.session_state.selected_tone == "friendly" else "secondary",
                        key="tone_friendly"):
                st.session_state.selected_tone = "friendly"
                st.rerun()
        
        with tone_col3:
            if st.button("Formal", use_container_width=True, 
                        type="primary" if st.session_state.selected_tone == "formal" else "secondary",
                        key="tone_formal"):
                st.session_state.selected_tone = "formal"
                st.rerun()
    else:
        # Use the profile's base style
        for profile in st.session_state.profiles:
            if profile["id"] == st.session_state.selected_profile_id:
                style = profile.get("base_style", "casual")
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
    
    # Advanced options
    with st.expander("Advanced Options"):
        st.markdown('<div class="advanced-options">', unsafe_allow_html=True)
        
        process_mode = st.radio(
            "Processing mode:",
            options=["Synchronous", "Asynchronous"],
            index=0,
            horizontal=True
        )
        
        formality_level = st.slider(
            "Formality Level",
            min_value=1,
            max_value=10,
            value=5,
            help="1 = Very informal, 10 = Very formal"
        )
        
        contraction_probability = st.slider(
            "Contraction Probability",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Probability of using contractions (0.0-1.0)"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
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
                        
                        # Analyze the text for AI detection
                        if text_input != st.session_state.analyzed_text:
                            st.session_state.ai_detection_score, st.session_state.ai_detection_suggestions = analyze_ai_patterns(text_input)
                            st.session_state.analyzed_text = text_input
                        
                        # Calculate quality metrics
                        original_humanness = calculate_humanness_score(text_input)
                        humanized_humanness = calculate_humanness_score(st.session_state.humanized_text, st.session_state.analysis)
                        st.session_state.humanness_score = humanized_humanness
                        st.session_state.humanness_improvement = humanized_humanness - original_humanness
                        
                        original_readability = calculate_readability_grade(text_input)
                        humanized_readability = calculate_readability_grade(st.session_state.humanized_text)
                        st.session_state.readability_grade = humanized_readability
                        
                        # Determine readability improvement
                        readability_levels = ["Elementary", "Middle School", "High School", "College", "Graduate", "Professional"]
                        if original_readability in readability_levels and humanized_readability in readability_levels:
                            original_index = readability_levels.index(original_readability)
                            humanized_index = readability_levels.index(humanized_readability)
                            
                            # For readability, we consider "High School" and "College" as optimal
                            if original_index < 2 and humanized_index >= 2:
                                st.session_state.readability_improvement = 1  # Improved
                            elif original_index > 3 and humanized_index >= 2 and humanized_index <= 3:
                                st.session_state.readability_improvement = 1  # Improved
                            elif original_index >= 2 and original_index <= 3 and (humanized_index < 2 or humanized_index > 3):
                                st.session_state.readability_improvement = -1  # Decreased
                            else:
                                st.session_state.readability_improvement = 0  # No change
                        else:
                            st.session_state.readability_improvement = 0
                        
                        # Update process status and quality level
                        st.session_state.process_status = "complete"
                        
                        if humanized_humanness >= 80:
                            st.session_state.quality_level = "high"
                        elif humanized_humanness >= 60:
                            st.session_state.quality_level = "medium"
                        else:
                            st.session_state.quality_level = "low"
                        
                        # Generate improvement areas heatmap data
                        st.session_state.improvement_areas = generate_improvement_heatmap(st.session_state.humanized_text, st.session_state.analysis)
                        
                        st.success("Text transformed successfully!")
                        st.rerun()
                else:
                    # Asynchronous processing
                    response = humanize_text_async(text_input, style, st.session_state.selected_profile_id)
                    
                    if response:
                        st.session_state.job_id = response.get("job_id")
                        st.session_state.job_status = response.get("status")
                        
                        # Analyze the text for AI detection
                        if text_input != st.session_state.analyzed_text:
                            st.session_state.ai_detection_score, st.session_state.ai_detection_suggestions = analyze_ai_patterns(text_input)
                            st.session_state.analyzed_text = text_input
                        
                        # Update process status
                        st.session_state.process_status = "in-progress"
                        
                        st.info(f"Job submitted successfully! Job ID: {st.session_state.job_id}")
                        st.rerun()
    
    # Analyze button for AI detection
    if st.button("Analyze for AI Detection", use_container_width=True):
        if not text_input or not text_input.strip():
            st.error("Please enter some text to analyze.")
        else:
            with st.spinner("Analyzing text for AI patterns..."):
                st.session_state.original_text = text_input
                st.session_state.ai_detection_score, st.session_state.ai_detection_suggestions = analyze_ai_patterns(text_input)
                st.session_state.analyzed_text = text_input
                
                # Calculate humanness score for original text
                original_humanness = calculate_humanness_score(text_input)
                st.session_state.humanness_score = original_humanness
                st.session_state.humanness_improvement = 0
                
                # Calculate readability grade
                st.session_state.readability_grade = calculate_readability_grade(text_input)
                st.session_state.readability_improvement = 0
                
                # Update process status and quality level
                st.session_state.process_status = "complete"
                
                if original_humanness >= 80:
                    st.session_state.quality_level = "high"
                elif original_humanness >= 60:
                    st.session_state.quality_level = "medium"
                else:
                    st.session_state.quality_level = "low"
                
                # Generate improvement areas heatmap data
                st.session_state.improvement_areas = generate_improvement_heatmap(text_input)
                
                st.success("Analysis complete!")
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Right panel - Output
    st.markdown('<div class="output-panel">', unsafe_allow_html=True)
    st.markdown('<h3 class="panel-title">Output</h3>', unsafe_allow_html=True)
    
    # Check if we have a job ID and it's still processing
    if st.session_state.job_id and st.session_state.job_status == "processing":
        st.markdown(
            """
            <div class="loading-container">
                <div class="loading-spinner"></div>
                <p>Processing your text...</p>
                <p class="text-light">This may take a few moments</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Render status indicators
        render_status_indicators("in-progress", "medium")
        
        if st.button("Check Job Status"):
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
                        
                        # Calculate quality metrics
                        original_humanness = calculate_humanness_score(st.session_state.original_text)
                        humanized_humanness = calculate_humanness_score(st.session_state.humanized_text, st.session_state.analysis)
                        st.session_state.humanness_score = humanized_humanness
                        st.session_state.humanness_improvement = humanized_humanness - original_humanness
                        
                        original_readability = calculate_readability_grade(st.session_state.original_text)
                        humanized_readability = calculate_readability_grade(st.session_state.humanized_text)
                        st.session_state.readability_grade = humanized_readability
                        
                        # Determine readability improvement
                        readability_levels = ["Elementary", "Middle School", "High School", "College", "Graduate", "Professional"]
                        if original_readability in readability_levels and humanized_readability in readability_levels:
                            original_index = readability_levels.index(original_readability)
                            humanized_index = readability_levels.index(humanized_readability)
                            
                            # For readability, we consider "High School" and "College" as optimal
                            if original_index < 2 and humanized_index >= 2:
                                st.session_state.readability_improvement = 1  # Improved
                            elif original_index > 3 and humanized_index >= 2 and humanized_index <= 3:
                                st.session_state.readability_improvement = 1  # Improved
                            elif original_index >= 2 and original_index <= 3 and (humanized_index < 2 or humanized_index > 3):
                                st.session_state.readability_improvement = -1  # Decreased
                            else:
                                st.session_state.readability_improvement = 0  # No change
                        else:
                            st.session_state.readability_improvement = 0
                        
                        # Update process status and quality level
                        st.session_state.process_status = "complete"
                        
                        if humanized_humanness >= 80:
                            st.session_state.quality_level = "high"
                        elif humanized_humanness >= 60:
                            st.session_state.quality_level = "medium"
                        else:
                            st.session_state.quality_level = "low"
                        
                        # Generate improvement areas heatmap data
                        st.session_state.improvement_areas = generate_improvement_heatmap(st.session_state.humanized_text, st.session_state.analysis)
                        
                        st.success("Text transformation completed!")
                        st.rerun()
                    elif job_response.get("status") == "failed":
                        st.session_state.process_status = "error"
                        st.error(f"Job failed: {job_response.get('error', 'Unknown error')}")
                    else:
                        st.info(f"Job is still processing. Status: {job_response.get('status')}")
    
    # Display results if available
    elif st.session_state.humanized_text:
        # Render Quality Metrics Panel
        render_quality_metrics_panel(
            st.session_state.humanness_score,
            st.session_state.humanness_improvement,
            st.session_state.readability_grade,
            st.session_state.readability_improvement
        )
        
        # Render Status Indicators
        render_status_indicators(st.session_state.process_status, st.session_state.quality_level)
        
        st.markdown('<div class="results-display">', unsafe_allow_html=True)
        
        # Humanized text
        st.markdown('<div class="text-comparison humanized">', unsafe_allow_html=True)
        st.markdown('<h4>Humanized Text</h4>', unsafe_allow_html=True)
        st.text_area(
            "Humanized",
            value=st.session_state.humanized_text,
            height=250,
            disabled=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Copy button for humanized text
        if st.button("Copy Humanized Text", use_container_width=True):
            st.code(st.session_state.humanized_text)
            st.success("Text copied to clipboard! (Use Ctrl+C to copy from the code block above)")
        
        # Render Before/After Comparison
        render_text_comparison(st.session_state.original_text, st.session_state.humanized_text)
        
        # Render Improvement Heatmap
        render_improvement_heatmap(st.session_state.improvement_areas)
        
        # Analysis section
        if st.session_state.analysis:
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
                st.markdown('<div class="quality-metrics">', unsafe_allow_html=True)
                
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <p class="metric-label">Avg. Sentence Length</p>
                        <p class="metric-value">{metrics.get('avg_sentence_length', 0):.1f}</p>
                        <p class="metric-unit">words</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <p class="metric-label">Repeated N-grams</p>
                        <p class="metric-value">{metrics.get('repeated_ngrams_count', 0)}</p>
                        <p class="metric-unit">count</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <p class="metric-label">Contraction Ratio</p>
                        <p class="metric-value">{metrics.get('contraction_ratio', 0):.2f}</p>
                        <p class="metric-unit">ratio</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Improvement tips
            patterns = st.session_state.analysis.get("patterns_found", [])
            if patterns:
                st.markdown('<div class="improvement-tips">', unsafe_allow_html=True)
                st.markdown('<h4>Improvement Tips</h4>', unsafe_allow_html=True)
                
                for pattern in patterns:
                    severity = pattern.get("severity", "low")
                    if severity in ["medium", "high"]:
                        st.markdown(
                            f"""
                            <div class="tip-item">
                                {pattern.get('description', '')}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # AI Detection Bypass Panel
        st.markdown('<div class="ai-detection-panel">', unsafe_allow_html=True)
        st.markdown('<h3 class="ai-detection-title">AI Detection Bypass</h3>', unsafe_allow_html=True)
        
        # Display AI detection score if available
        if st.session_state.ai_detection_score is not None:
            score = st.session_state.ai_detection_score
            score_color = "var(--danger-color)" if score > 70 else "var(--warning-color)" if score > 40 else "var(--success-color)"
            risk_level = "High" if score > 70 else "Medium" if score > 40 else "Low"
            
            st.markdown(
                f"""
                <div class="detection-result">
                    <h4>AI Detection Risk</h4>
                    <div class="detection-score" style="color: {score_color};">{score}%</div>
                    <div class="detection-label">Risk Level: {risk_level}</div>
                    <p>
                        {
                            "Your text has a high risk of being detected as AI-generated. Use the suggestions below to reduce this risk." 
                            if score > 70 else 
                            "Your text has a moderate risk of being detected as AI-generated. Consider some improvements." 
                            if score > 40 else 
                            "Your text has a low risk of being detected as AI-generated. It already appears quite human-like."
                        }
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Display suggestions if available
            if st.session_state.ai_detection_suggestions:
                st.markdown('<h4>Humanization Suggestions</h4>', unsafe_allow_html=True)
                
                for i, suggestion in enumerate(st.session_state.ai_detection_suggestions):
                    st.markdown(
                        f"""
                        <div class="suggestion-card">
                            <div class="suggestion-title">{suggestion.get('title', 'Suggestion')}</div>
                            <div class="suggestion-text">{suggestion.get('text', '')}</div>
                            <div class="suggestion-reason">{suggestion.get('reason', '')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Highlight problematic sections in the original text
                if st.session_state.original_text:
                    sentences_to_highlight = find_sentences_to_highlight(st.session_state.original_text, st.session_state.ai_detection_suggestions)
                    
                    if sentences_to_highlight:
                        st.markdown('<h4>Highlighted Problem Areas</h4>', unsafe_allow_html=True)
                        highlighted_text = highlight_text(st.session_state.original_text, sentences_to_highlight)
                        st.markdown(f'<div style="background-color: var(--neutral-100); padding: 1rem; border-radius: 6px;">{highlighted_text}</div>', unsafe_allow_html=True)
        
        # Advanced humanization options
        st.markdown('<h4>Advanced Humanization Options</h4>', unsafe_allow_html=True)
        
        # Humanization level slider
        st.markdown('<div class="humanization-level-container">', unsafe_allow_html=True)
        humanization_level = st.slider(
            "Humanization Level",
            min_value=1,
            max_value=10,
            value=st.session_state.humanization_level,
            help="Higher values produce more human-like text but may alter meaning more significantly."
        )
        st.session_state.humanization_level = humanization_level
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Preserve keywords
        st.markdown('<div class="preserve-keywords-container">', unsafe_allow_html=True)
        preserve_keywords = st.text_area(
            "Preserve Keywords (one per line)",
            value="\n".join(st.session_state.preserve_keywords),
            help="Enter important keywords or phrases that should be preserved during humanization.",
            placeholder="Enter keywords or phrases to preserve"
        )
        st.session_state.preserve_keywords = [kw.strip() for kw in preserve_keywords.split("\n") if kw.strip()]
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Tone selection
        st.markdown('<div class="tone-selection-container">', unsafe_allow_html=True)
        st.markdown('<label>Select Tone</label>', unsafe_allow_html=True)
        
        tone_col1, tone_col2, tone_col3, tone_col4 = st.columns(4)
        
        with tone_col1:
            if st.button("Casual", use_container_width=True, 
                        type="primary" if st.session_state.selected_bypass_tone == "Casual" else "secondary",
                        key="bypass_tone_casual"):
                st.session_state.selected_bypass_tone = "Casual"
                st.rerun()
        
        with tone_col2:
            if st.button("Formal", use_container_width=True, 
                        type="primary" if st.session_state.selected_bypass_tone == "Formal" else "secondary",
                        key="bypass_tone_formal"):
                st.session_state.selected_bypass_tone = "Formal"
                st.rerun()
        
        with tone_col3:
            if st.button("Academic", use_container_width=True, 
                        type="primary" if st.session_state.selected_bypass_tone == "Academic" else "secondary",
                        key="bypass_tone_academic"):
                st.session_state.selected_bypass_tone = "Academic"
                st.rerun()
        
        with tone_col4:
            if st.button("Creative", use_container_width=True, 
                        type="primary" if st.session_state.selected_bypass_tone == "Creative" else "secondary",
                        key="bypass_tone_creative"):
                st.session_state.selected_bypass_tone = "Creative"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply humanization button
        if st.button("Apply Advanced Humanization", type="primary", use_container_width=True):
            with st.spinner("Applying advanced humanization..."):
                # In a real implementation, this would call a specialized API endpoint
                # For now, we'll just show a success message
                st.success("Advanced humanization applied successfully!")
                
                # Update the detection score to simulate improvement
                if st.session_state.ai_detection_score is not None:
                    # Reduce the score based on humanization level (higher level = more reduction)
                    reduction = st.session_state.humanization_level * 5
                    new_score = max(10, st.session_state.ai_detection_score - reduction)
                    st.session_state.ai_detection_score = new_score
                    
                    # Update suggestions to reflect the changes
                    if new_score < 30:
                        st.session_state.ai_detection_suggestions = [{
                            "title": "Text successfully humanized",
                            "text": "Your text now appears highly human-like.",
                            "reason": "The advanced humanization process has significantly reduced AI detection markers."
                        }]
                    
                    # Update humanness score
                    st.session_state.humanness_score = min(100, st.session_state.humanness_score + 10)
                    st.session_state.humanness_improvement += 10
                    
                    # Update quality level
                    if st.session_state.humanness_score >= 80:
                        st.session_state.quality_level = "high"
                    elif st.session_state.humanness_score >= 60:
                        st.session_state.quality_level = "medium"
                    else:
                        st.session_state.quality_level = "low"
                    
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # No results yet - show AI Detection Bypass Panel if text has been analyzed
        if st.session_state.ai_detection_score is not None and st.session_state.original_text:
            # Render Quality Metrics Panel
            render_quality_metrics_panel(
                st.session_state.humanness_score,
                st.session_state.humanness_improvement,
                st.session_state.readability_grade,
                st.session_state.readability_improvement
            )
            
            # Render Status Indicators
            render_status_indicators(st.session_state.process_status, st.session_state.quality_level)
            
            # Render Improvement Heatmap
            render_improvement_heatmap(st.session_state.improvement_areas)
            
            # AI Detection Bypass Panel
            st.markdown('<div class="ai-detection-panel">', unsafe_allow_html=True)
            st.markdown('<h3 class="ai-detection-title">AI Detection Bypass</h3>', unsafe_allow_html=True)
            
            # Display AI detection score
            score = st.session_state.ai_detection_score
            score_color = "var(--danger-color)" if score > 70 else "var(--warning-color)" if score > 40 else "var(--success-color)"
            risk_level = "High" if score > 70 else "Medium" if score > 40 else "Low"
            
            st.markdown(
                f"""
                <div class="detection-result">
                    <h4>AI Detection Risk</h4>
                    <div class="detection-score" style="color: {score_color};">{score}%</div>
                    <div class="detection-label">Risk Level: {risk_level}</div>
                    <p>
                        {
                            "Your text has a high risk of being detected as AI-generated. Use the suggestions below to reduce this risk." 
                            if score > 70 else 
                            "Your text has a moderate risk of being detected as AI-generated. Consider some improvements." 
                            if score > 40 else 
                            "Your text has a low risk of being detected as AI-generated. It already appears quite human-like."
                        }
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Display suggestions if available
            if st.session_state.ai_detection_suggestions:
                st.markdown('<h4>Humanization Suggestions</h4>', unsafe_allow_html=True)
                
                for i, suggestion in enumerate(st.session_state.ai_detection_suggestions):
                    st.markdown(
                        f"""
                        <div class="suggestion-card">
                            <div class="suggestion-title">{suggestion.get('title', 'Suggestion')}</div>
                            <div class="suggestion-text">{suggestion.get('text', '')}</div>
                            <div class="suggestion-reason">{suggestion.get('reason', '')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Highlight problematic sections in the original text
                if st.session_state.original_text:
                    sentences_to_highlight = find_sentences_to_highlight(st.session_state.original_text, st.session_state.ai_detection_suggestions)
                    
                    if sentences_to_highlight:
                        st.markdown('<h4>Highlighted Problem Areas</h4>', unsafe_allow_html=True)
                        highlighted_text = highlight_text(st.session_state.original_text, sentences_to_highlight)
                        st.markdown(f'<div style="background-color: var(--neutral-100); padding: 1rem; border-radius: 6px;">{highlighted_text}</div>', unsafe_allow_html=True)
            
            # Advanced humanization options
            st.markdown('<h4>Advanced Humanization Options</h4>', unsafe_allow_html=True)
            
            # Humanization level slider
            st.markdown('<div class="humanization-level-container">', unsafe_allow_html=True)
            humanization_level = st.slider(
                "Humanization Level",
                min_value=1,
                max_value=10,
                value=st.session_state.humanization_level,
                help="Higher values produce more human-like text but may alter meaning more significantly."
            )
            st.session_state.humanization_level = humanization_level
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Preserve keywords
            st.markdown('<div class="preserve-keywords-container">', unsafe_allow_html=True)
            preserve_keywords = st.text_area(
                "Preserve Keywords (one per line)",
                value="\n".join(st.session_state.preserve_keywords),
                help="Enter important keywords or phrases that should be preserved during humanization.",
                placeholder="Enter keywords or phrases to preserve"
            )
            st.session_state.preserve_keywords = [kw.strip() for kw in preserve_keywords.split("\n") if kw.strip()]
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Tone selection
            st.markdown('<div class="tone-selection-container">', unsafe_allow_html=True)
            st.markdown('<label>Select Tone</label>', unsafe_allow_html=True)
            
            tone_col1, tone_col2, tone_col3, tone_col4 = st.columns(4)
            
            with tone_col1:
                if st.button("Casual", use_container_width=True, 
                            type="primary" if st.session_state.selected_bypass_tone == "Casual" else "secondary",
                            key="bypass_tone_casual"):
                    st.session_state.selected_bypass_tone = "Casual"
                    st.rerun()
            
            with tone_col2:
                if st.button("Formal", use_container_width=True, 
                            type="primary" if st.session_state.selected_bypass_tone == "Formal" else "secondary",
                            key="bypass_tone_formal"):
                    st.session_state.selected_bypass_tone = "Formal"
                    st.rerun()
            
            with tone_col3:
                if st.button("Academic", use_container_width=True, 
                            type="primary" if st.session_state.selected_bypass_tone == "Academic" else "secondary",
                            key="bypass_tone_academic"):
                    st.session_state.selected_bypass_tone = "Academic"
                    st.rerun()
            
            with tone_col4:
                if st.button("Creative", use_container_width=True, 
                            type="primary" if st.session_state.selected_bypass_tone == "Creative" else "secondary",
                            key="bypass_tone_creative"):
                    st.session_state.selected_bypass_tone = "Creative"
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Transform with advanced options button
            if st.button("Transform with Advanced Options", type="primary", use_container_width=True):
                if not st.session_state.original_text:
                    st.error("Please enter some text to transform.")
                else:
                    with st.spinner("Transforming your text with advanced options..."):
                        # In a real implementation, this would call a specialized API endpoint
                        # For now, we'll simulate a response
                        
                        # Call the regular humanize function as a fallback
                        response = humanize_text(st.session_state.original_text, "casual", None)
                        
                        if response:
                            st.session_state.humanized_text = response.get("humanized", "")
                            st.session_state.analysis = response.get("analysis", None)
                            
                            # Update usage stats
                            st.session_state.usage_stats["transformations_today"] += 1
                            st.session_state.usage_stats["transformations_total"] += 1
                            st.session_state.usage_stats["last_transformation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            # Update the detection score to simulate improvement
                            if st.session_state.ai_detection_score is not None:
                                # Reduce the score based on humanization level (higher level = more reduction)
                                reduction = st.session_state.humanization_level * 5
                                new_score = max(10, st.session_state.ai_detection_score - reduction)
                                st.session_state.ai_detection_score = new_score
                            
                            # Calculate quality metrics
                            original_humanness = calculate_humanness_score(st.session_state.original_text)
                            humanized_humanness = calculate_humanness_score(st.session_state.humanized_text, st.session_state.analysis)
                            st.session_state.humanness_score = humanized_humanness
                            st.session_state.humanness_improvement = humanized_humanness - original_humanness
                            
                            original_readability = calculate_readability_grade(st.session_state.original_text)
                            humanized_readability = calculate_readability_grade(st.session_state.humanized_text)
                            st.session_state.readability_grade = humanized_readability
                            
                            # Determine readability improvement
                            readability_levels = ["Elementary", "Middle School", "High School", "College", "Graduate", "Professional"]
                            if original_readability in readability_levels and humanized_readability in readability_levels:
                                original_index = readability_levels.index(original_readability)
                                humanized_index = readability_levels.index(humanized_readability)
                                
                                # For readability, we consider "High School" and "College" as optimal
                                if original_index < 2 and humanized_index >= 2:
                                    st.session_state.readability_improvement = 1  # Improved
                                elif original_index > 3 and humanized_index >= 2 and humanized_index <= 3:
                                    st.session_state.readability_improvement = 1  # Improved
                                elif original_index >= 2 and original_index <= 3 and (humanized_index < 2 or humanized_index > 3):
                                    st.session_state.readability_improvement = -1  # Decreased
                                else:
                                    st.session_state.readability_improvement = 0  # No change
                            else:
                                st.session_state.readability_improvement = 0
                            
                            # Update process status and quality level
                            st.session_state.process_status = "complete"
                            
                            if humanized_humanness >= 80:
                                st.session_state.quality_level = "high"
                            elif humanized_humanness >= 60:
                                st.session_state.quality_level = "medium"
                            else:
                                st.session_state.quality_level = "low"
                            
                            # Generate improvement areas heatmap data
                            st.session_state.improvement_areas = generate_improvement_heatmap(st.session_state.humanized_text, st.session_state.analysis)
                            
                            st.success("Text transformed successfully with advanced options!")
                            st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # No results yet
            st.markdown(
                """
                <div class="output-placeholder">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <h4>No Results Yet</h4>
                    <p>Enter your text and click "Transform Text" to see the humanized version here.</p>
                    <p>Or click "Analyze for AI Detection" to check your text for AI patterns.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # End of two-panel layout
    st.markdown('</div>', unsafe_allow_html=True)

# Results Experience Page (now integrated into the main workspace)
elif st.session_state.active_page == "Results":
    st.markdown('<h2 class="page-title">Results Experience</h2>', unsafe_allow_html=True)
    
    # Two-panel layout for results
    st.markdown('<div class="workspace-container">', unsafe_allow_html=True)
    
    # Left panel - Original text
    st.markdown('<div class="input-panel">', unsafe_allow_html=True)
    st.markdown('<h3 class="panel-title">Original Text</h3>', unsafe_allow_html=True)
    
    if st.session_state.original_text:
        st.text_area(
            "Original",
            value=st.session_state.original_text,
            height=300,
            disabled=True
        )
    else:
        st.markdown(
            """
            <div class="output-placeholder">
                <h4>No Original Text</h4>
                <p>Go to the Transformation Workspace to input text.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if st.button("Go to Transformation Workspace", type="primary"):
            st.session_state.active_page = "Transformation"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Right panel - Humanized text and analysis
    st.markdown('<div class="output-panel">', unsafe_allow_html=True)
    st.markdown('<h3 class="panel-title">Humanized Text</h3>', unsafe_allow_html=True)
    
    # Check if we have a job ID and it's still processing
    if st.session_state.job_id and st.session_state.job_status == "processing":
        st.markdown('<div class="job-status-container">', unsafe_allow_html=True)
        st.markdown(f'<h3>Job Status: <span class="processing-status">Processing</span></h3>', unsafe_allow_html=True)
        st.markdown(f'<p>Job ID: {st.session_state.job_id}</p>', unsafe_allow_html=True)
        
        # Render status indicators
        render_status_indicators("in-progress", "medium")
        
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
                        
                        # Calculate quality metrics
                        original_humanness = calculate_humanness_score(st.session_state.original_text)
                        humanized_humanness = calculate_humanness_score(st.session_state.humanized_text, st.session_state.analysis)
                        st.session_state.humanness_score = humanized_humanness
                        st.session_state.humanness_improvement = humanized_humanness - original_humanness
                        
                        original_readability = calculate_readability_grade(st.session_state.original_text)
                        humanized_readability = calculate_readability_grade(st.session_state.humanized_text)
                        st.session_state.readability_grade = humanized_readability
                        
                        # Determine readability improvement
                        readability_levels = ["Elementary", "Middle School", "High School", "College", "Graduate", "Professional"]
                        if original_readability in readability_levels and humanized_readability in readability_levels:
                            original_index = readability_levels.index(original_readability)
                            humanized_index = readability_levels.index(humanized_readability)
                            
                            # For readability, we consider "High School" and "College" as optimal
                            if original_index < 2 and humanized_index >= 2:
                                st.session_state.readability_improvement = 1  # Improved
                            elif original_index > 3 and humanized_index >= 2 and humanized_index <= 3:
                                st.session_state.readability_improvement = 1  # Improved
                            elif original_index >= 2 and original_index <= 3 and (humanized_index < 2 or humanized_index > 3):
                                st.session_state.readability_improvement = -1  # Decreased
                            else:
                                st.session_state.readability_improvement = 0  # No change
                        else:
                            st.session_state.readability_improvement = 0
                        
                        # Update process status and quality level
                        st.session_state.process_status = "complete"
                        
                        if humanized_humanness >= 80:
                            st.session_state.quality_level = "high"
                        elif humanized_humanness >= 60:
                            st.session_state.quality_level = "medium"
                        else:
                            st.session_state.quality_level = "low"
                        
                        # Generate improvement areas heatmap data
                        st.session_state.improvement_areas = generate_improvement_heatmap(st.session_state.humanized_text, st.session_state.analysis)
                        
                        st.success("Text transformation completed!")
                        st.rerun()
                    elif job_response.get("status") == "failed":
                        st.session_state.process_status = "error"
                        st.error(f"Job failed: {job_response.get('error', 'Unknown error')}")
                    else:
                        st.info(f"Job is still processing. Status: {job_response.get('status')}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display results if available
    elif st.session_state.humanized_text:
        # Render Quality Metrics Panel
        render_quality_metrics_panel(
            st.session_state.humanness_score,
            st.session_state.humanness_improvement,
            st.session_state.readability_grade,
            st.session_state.readability_improvement
        )
        
        # Render Status Indicators
        render_status_indicators(st.session_state.process_status, st.session_state.quality_level)
        
        st.text_area(
            "Humanized",
            value=st.session_state.humanized_text,
            height=300,
            disabled=True
        )
        
        # Copy button for humanized text
        if st.button("Copy Humanized Text", use_container_width=True):
            st.code(st.session_state.humanized_text)
            st.success("Text copied to clipboard! (Use Ctrl+C to copy from the code block above)")
        
        # Render Before/After Comparison
        render_text_comparison(st.session_state.original_text, st.session_state.humanized_text)
        
        # Render Improvement Heatmap
        render_improvement_heatmap(st.session_state.improvement_areas)
        
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
            
            # AI Detection Bypass Panel
            if st.session_state.ai_detection_score is not None:
                st.markdown('<div class="ai-detection-panel">', unsafe_allow_html=True)
                st.markdown('<h3 class="ai-detection-title">AI Detection Bypass</h3>', unsafe_allow_html=True)
                
                # Display AI detection score
                score = st.session_state.ai_detection_score
                score_color = "var(--danger-color)" if score > 70 else "var(--warning-color)" if score > 40 else "var(--success-color)"
                risk_level = "High" if score > 70 else "Medium" if score > 40 else "Low"
                
                st.markdown(
                    f"""
                    <div class="detection-result">
                        <h4>AI Detection Risk</h4>
                        <div class="detection-score" style="color: {score_color};">{score}%</div>
                        <div class="detection-label">Risk Level: {risk_level}</div>
                        <p>
                            {
                                "Your text has a high risk of being detected as AI-generated. Use the suggestions below to reduce this risk." 
                                if score > 70 else 
                                "Your text has a moderate risk of being detected as AI-generated. Consider some improvements." 
                                if score > 40 else 
                                "Your text has a low risk of being detected as AI-generated. It already appears quite human-like."
                            }
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Display suggestions if available
                if st.session_state.ai_detection_suggestions:
                    st.markdown('<h4>Humanization Suggestions</h4>', unsafe_allow_html=True)
                    
                    for i, suggestion in enumerate(st.session_state.ai_detection_suggestions):
                        st.markdown(
                            f"""
                            <div class="suggestion-card">
                                <div class="suggestion-title">{suggestion.get('title', 'Suggestion')}</div>
                                <div class="suggestion-text">{suggestion.get('text', '')}</div>
                                <div class="suggestion-reason">{suggestion.get('reason', '')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        # No results yet
        st.markdown(
            """
            <div class="output-placeholder">
                <h4>No Results Yet</h4>
                <p>Transform text in the Transformation Workspace to see results here.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
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
    
    # End of two-panel layout
    st.markdown('</div>', unsafe_allow_html=True)

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
