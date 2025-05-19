
"""
Humanyzer AI Detection Bypass Panel
This file implements the AI Detection Bypass Panel with content analysis, suggestions, and advanced options.
"""
import streamlit as st
from services.text_service import analyze_ai_patterns
from components.detection import (
    render_detection_score,
    render_suggestions,
    highlight_text,
    find_sentences_to_highlight
)

def render_ai_detection_panel():
    """Render the AI Detection Bypass Panel"""
    st.markdown('<div class="ai-detection-panel">', unsafe_allow_html=True)
    st.markdown('<h3 class="ai-detection-title">AI Detection Bypass</h3>', unsafe_allow_html=True)
    
    # Detection score
    if st.session_state.ai_detection_score is not None:
        render_detection_score(st.session_state.ai_detection_score)
    
    # Suggestions
    if st.session_state.ai_detection_suggestions:
        st.markdown('<h4>Improvement Suggestions</h4>', unsafe_allow_html=True)
        render_suggestions(st.session_state.ai_detection_suggestions)
        
        # Highlight problematic sections in the original text
        if st.session_state.original_text:
            sentences_to_highlight = find_sentences_to_highlight(
                st.session_state.original_text, 
                st.session_state.ai_detection_suggestions
            )
            
            if sentences_to_highlight:
                st.markdown('<h4>Highlighted Problem Areas</h4>', unsafe_allow_html=True)
                highlighted_text = highlight_text(st.session_state.original_text, sentences_to_highlight)
                st.markdown(
                    f'<div style="background-color: var(--neutral-100); padding: 1rem; border-radius: 6px;">{highlighted_text}</div>', 
                    unsafe_allow_html=True
                )
    
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
                    type="primary" if st.session_state.selected_bypass_tone == "Casual" else "secondary"):
            st.session_state.selected_bypass_tone = "Casual"
            st.rerun()
    
    with tone_col2:
        if st.button("Professional", use_container_width=True, 
                    type="primary" if st.session_state.selected_bypass_tone == "Professional" else "secondary"):
            st.session_state.selected_bypass_tone = "Professional"
            st.rerun()
    
    with tone_col3:
        if st.button("Academic", use_container_width=True, 
                    type="primary" if st.session_state.selected_bypass_tone == "Academic" else "secondary"):
            st.session_state.selected_bypass_tone = "Academic"
            st.rerun()
    
    with tone_col4:
        if st.button("Creative", use_container_width=True, 
                    type="primary" if st.session_state.selected_bypass_tone == "Creative" else "secondary"):
            st.session_state.selected_bypass_tone = "Creative"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
