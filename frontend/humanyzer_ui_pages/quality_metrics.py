
"""
Humanyzer Quality Metrics Panel
This file implements the Quality Metrics Panel with visual risk indicators.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def render_quality_metrics_panel():
    """Render the Quality Metrics Panel with visual risk indicators"""
    st.markdown('<div class="quality-metrics-panel">', unsafe_allow_html=True)
    st.markdown('<h3 class="quality-metrics-title">Quality Metrics</h3>', unsafe_allow_html=True)
    
    # Humanness score
    humanness_score = st.session_state.humanness_score
    humanness_improvement = st.session_state.humanness_improvement
    
    # Determine score color
    if humanness_score >= 80:
        score_color = "var(--success-color)"
    elif humanness_score >= 60:
        score_color = "var(--warning-color)"
    else:
        score_color = "var(--danger-color)"
    
    # Determine improvement indicator
    if humanness_improvement > 0:
        improvement_indicator = "↑"
        improvement_color = "var(--success-color)"
    elif humanness_improvement < 0:
        improvement_indicator = "↓"
        improvement_color = "var(--danger-color)"
    else:
        improvement_indicator = "→"
        improvement_color = "var(--neutral-500)"
    
    # Render humanness score
    st.markdown(
        f"""
        <div class="humanness-score-container">
            <h4>Humanness Score</h4>
            <div class="score-display">
                <span class="score-value" style="color: {score_color};">{humanness_score}%</span>
                <span class="score-change" style="color: {improvement_color};">{improvement_indicator} {abs(humanness_improvement):.1f}%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Readability grade
    readability_grade = st.session_state.readability_grade
    readability_improvement = st.session_state.readability_improvement
    
    # Determine improvement indicator
    if readability_improvement > 0:
        readability_indicator = "Improved"
        readability_color = "var(--success-color)"
    elif readability_improvement < 0:
        readability_indicator = "Decreased"
        readability_color = "var(--danger-color)"
    else:
        readability_indicator = "No Change"
        readability_color = "var(--neutral-500)"
    
    # Render readability grade
    st.markdown(
        f"""
        <div class="readability-grade-container">
            <h4>Readability Grade</h4>
            <div class="grade-display">
                <span class="grade-value">{readability_grade}</span>
                <span class="grade-change" style="color: {readability_color};">{readability_indicator}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render status indicators
    render_status_indicators()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_status_indicators():
    """Render color-coded status indicators"""
    process_status = st.session_state.process_status
    quality_level = st.session_state.quality_level
    
    # Determine status colors
    if process_status == "complete":
        status_color = "var(--success-color)"
        status_text = "Complete"
    elif process_status == "in-progress":
        status_color = "var(--warning-color)"
        status_text = "In Progress"
    else:
        status_color = "var(--neutral-500)"
        status_text = "Not Started"
    
    # Determine quality colors
    if quality_level == "high":
        quality_color = "var(--success-color)"
        quality_text = "High"
    elif quality_level == "medium":
        quality_color = "var(--warning-color)"
        quality_text = "Medium"
    else:
        quality_color = "var(--danger-color)"
        quality_text = "Low"
    
    # Render status indicators
    st.markdown(
        f"""
        <div class="status-indicators">
            <div class="status-indicator">
                <span class="indicator-label">Process Status:</span>
                <span class="indicator-value" style="color: {status_color};">{status_text}</span>
            </div>
            <div class="status-indicator">
                <span class="indicator-label">Quality Level:</span>
                <span class="indicator-value" style="color: {quality_color};">{quality_text}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_improvement_heatmap(heatmap_data):
    """Render heatmap-style visualization for improvement areas"""
    if not heatmap_data or not heatmap_data.get("paragraphs") or not heatmap_data.get("categories") or not heatmap_data.get("values"):
        return
    
    st.markdown('<div class="heatmap-container">', unsafe_allow_html=True)
    st.markdown('<h4 class="heatmap-title">Improvement Areas</h4>', unsafe_allow_html=True)
    
    # Create heatmap data
    paragraphs = heatmap_data["paragraphs"]
    categories = heatmap_data["categories"]
    values = heatmap_data["values"]
    
    # Create a DataFrame for the heatmap
    heatmap_df = pd.DataFrame(values, columns=categories)
    
    # Create the heatmap
    fig = px.imshow(
        heatmap_df,
        labels=dict(x="Category", y="Paragraph", color="Improvement Needed"),
        x=categories,
        y=paragraphs,
        color_continuous_scale=["#10B981", "#FBBF24", "#EF4444"],
        aspect="auto",
        height=max(200, len(paragraphs) * 30)
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title="Improvement<br>Needed",
            tickvals=[0.2, 0.5, 0.8],
            ticktext=["Low", "Medium", "High"],
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
