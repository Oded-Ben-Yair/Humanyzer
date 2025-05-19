"""
Humanyzer Main Workspace UI Page
This file implements the two-panel layout structure for the main workspace with enhanced accessibility and mobile responsiveness.
"""
import streamlit as st
import os

def render_main_workspace():
    """Render the main workspace with two-panel layout and enhanced accessibility"""
    # Load custom workspace CSS
    workspace_css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workspace.css")
    if os.path.exists(workspace_css_path):
        with open(workspace_css_path) as f:
            workspace_css = f.read()
            st.markdown(f"<style>{workspace_css}</style>", unsafe_allow_html=True)
    
    # Load mobile JavaScript enhancements
    mobile_js_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mobile.js")
    if os.path.exists(mobile_js_path):
        with open(mobile_js_path) as f:
            mobile_js = f.read()
            st.components.v1.html(f"<script>{mobile_js}</script>", height=0)
    
    # Page title with ARIA attributes
    st.markdown(
        '<h2 class="page-title" id="workspace-title" role="heading" aria-level="2">Transformation Workspace</h2>', 
        unsafe_allow_html=True
    )
    
    # Context panel with improved accessibility
    with st.expander("About Transformation", expanded=False):
        st.markdown(
            """
            <div role="region" aria-label="Transformation Instructions">
                <p>The Transformation Workspace is where you can convert AI-generated text to sound more human.</p>
                
                <ul aria-label="Transformation Steps">
                    <li>Choose a style profile or use the basic styles</li>
                    <li>Paste your text and select processing options</li>
                    <li>Click "Transform" to humanize your content</li>
                </ul>
                
                <p>Your transformed text will appear in the right panel.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Two-panel layout container with ARIA attributes
    st.markdown(
        '<div class="workspace-container" role="main" aria-label="Transformation Workspace">', 
        unsafe_allow_html=True
    )
    
    # Left panel - Input with ARIA attributes
    st.markdown(
        '<div class="input-panel" role="region" aria-labelledby="input-panel-title">', 
        unsafe_allow_html=True
    )
    st.markdown(
        '<h3 class="panel-title" id="input-panel-title" tabindex="0">Input</h3>', 
        unsafe_allow_html=True
    )
    
    # Render input panel content
    render_input_panel()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Right panel - Output with ARIA attributes
    st.markdown(
        '<div class="output-panel" role="region" aria-labelledby="output-panel-title">', 
        unsafe_allow_html=True
    )
    st.markdown(
        '<h3 class="panel-title" id="output-panel-title" tabindex="0">Output</h3>', 
        unsafe_allow_html=True
    )
    
    # Render output panel content
    render_output_panel()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # End of two-panel layout
    st.markdown('</div>', unsafe_allow_html=True)

def render_input_panel():
    """Render the input panel with enhanced accessibility"""
    # Text input area with ARIA attributes
    text_input = st.text_area(
        "Paste your AI-generated text here:",
        height=250,
        key="text_input",
        value=st.session_state.get("original_text", ""),
        placeholder="Enter or paste your AI-generated text here. The more text you provide, the better the transformation will be.",
        help="This is where you enter the text you want to transform"
    )
    
    # Add ARIA attributes to the text area using JavaScript
    st.markdown(
        """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Find the text area and add ARIA attributes
                const textAreas = document.querySelectorAll('textarea');
                textAreas.forEach(textarea => {
                    textarea.setAttribute('aria-label', 'AI-generated text input');
                    textarea.setAttribute('aria-required', 'true');
                    textarea.setAttribute('aria-multiline', 'true');
                });
            });
        </script>
        """,
        unsafe_allow_html=True
    )
    
    # Options with responsive layout and ARIA attributes
    st.markdown('<div class="options-container" role="group" aria-label="Transformation Options">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="style-selector" role="region" aria-label="Style Selection">', unsafe_allow_html=True)
        style = st.selectbox(
            "Select writing style:",
            options=["casual", "professional", "creative"],
            index=0,
            help="Choose the writing style for your transformed text"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="process-mode-selector" role="region" aria-label="Processing Mode">', unsafe_allow_html=True)
        process_mode = st.radio(
            "Processing mode:",
            options=["Synchronous", "Asynchronous"],
            index=0,
            horizontal=True,
            help="Synchronous processing is immediate but may take longer. Asynchronous processing runs in the background."
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Submit button with ARIA attributes
    transform_button = st.button(
        "Humanize Text", 
        type="primary", 
        use_container_width=True,
        help="Click to transform your text"
    )
    
    # Add ARIA attributes to the button using JavaScript
    st.markdown(
        """
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Find the transform button and add ARIA attributes
                const buttons = document.querySelectorAll('button');
                buttons.forEach(button => {
                    if (button.textContent.includes('Humanize Text')) {
                        button.setAttribute('aria-label', 'Transform text to sound more human');
                        button.setAttribute('role', 'button');
                    }
                });
            });
        </script>
        """,
        unsafe_allow_html=True
    )
    
    # Store the input in session state if the button is clicked
    if transform_button:
        if not text_input or not text_input.strip():
            st.error("Please enter some text to humanize.")
        else:
            st.session_state["original_text"] = text_input
            
            # In a real implementation, this would call the API
            # For now, we'll just show a success message
            with st.spinner("Transforming your text..."):
                st.success("Text transformed successfully!")
                
                # Set a placeholder transformed text
                if "humanized_text" not in st.session_state:
                    st.session_state["humanized_text"] = "This is a placeholder for the humanized text. In a real implementation, this would be the result from the API."

def render_output_panel():
    """Render the output panel with enhanced accessibility"""
    # Check if we have humanized text to display
    if "humanized_text" in st.session_state and st.session_state["humanized_text"]:
        # Render status indicators with ARIA attributes
        render_status_indicators()
        
        # Display humanized text with ARIA attributes
        st.markdown('<div class="text-comparison humanized" role="region" aria-label="Humanized Text Result">', unsafe_allow_html=True)
        st.markdown('<h4 id="humanized-text-heading" tabindex="0">Humanized Text</h4>', unsafe_allow_html=True)
        
        st.text_area(
            "Humanized",
            value=st.session_state["humanized_text"],
            height=250,
            disabled=True,
            help="This is the transformed, more human-like version of your text"
        )
        
        # Add ARIA attributes to the text area using JavaScript
        st.markdown(
            """
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    // Find the humanized text area and add ARIA attributes
                    const textAreas = document.querySelectorAll('textarea');
                    textAreas.forEach(textarea => {
                        if (textarea.disabled) {
                            textarea.setAttribute('aria-label', 'Humanized text output');
                            textarea.setAttribute('aria-readonly', 'true');
                            textarea.setAttribute('aria-describedby', 'humanized-text-heading');
                        }
                    });
                });
            </script>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Copy button with ARIA attributes
        copy_button = st.button(
            "Copy Humanized Text", 
            use_container_width=True,
            help="Click to copy the humanized text to clipboard"
        )
        
        # Add ARIA attributes to the button using JavaScript
        st.markdown(
            """
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    // Find the copy button and add ARIA attributes
                    const buttons = document.querySelectorAll('button');
                    buttons.forEach(button => {
                        if (button.textContent.includes('Copy Humanized Text')) {
                            button.setAttribute('aria-label', 'Copy humanized text to clipboard');
                            button.setAttribute('role', 'button');
                        }
                    });
                });
            </script>
            """,
            unsafe_allow_html=True
        )
        
        if copy_button:
            st.code(st.session_state["humanized_text"])
            st.success("Text copied to clipboard! (Use Ctrl+C to copy from the code block above)")
        
        # Render text comparison with ARIA attributes
        render_text_comparison()
        
        # Render improvement heatmap with ARIA attributes
        render_improvement_heatmap()
    else:
        # No results yet - show placeholder with ARIA attributes
        st.markdown(
            """
            <div class="output-placeholder" role="region" aria-label="No Results Yet">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <h4 tabindex="0">No Results Yet</h4>
                <p>Enter your text and click "Transform Text" to see the humanized version here.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

def render_status_indicators():
    """Render status indicators with enhanced accessibility"""
    st.markdown('<div class="status-indicators" role="region" aria-label="Process Status">', unsafe_allow_html=True)
    
    # Process Status Indicator with ARIA attributes
    st.markdown(
        """
        <div class="status-indicator status-complete" role="status" aria-live="polite">
            <div class="status-indicator-dot" aria-hidden="true"></div>
            <span>Process Complete</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Quality Level Indicator with ARIA attributes
    st.markdown(
        """
        <div class="status-indicator status-complete" role="status" aria-live="polite">
            <div class="status-indicator-dot" aria-hidden="true"></div>
            <span>High Quality</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_text_comparison():
    """Render text comparison with enhanced accessibility"""
    if "original_text" in st.session_state and "humanized_text" in st.session_state:
        st.markdown('<div class="comparison-container" role="region" aria-labelledby="comparison-title">', unsafe_allow_html=True)
        st.markdown('<h4 id="comparison-title" class="comparison-title" tabindex="0">Before/After Comparison</h4>', unsafe_allow_html=True)
        
        # Create a simple comparison display
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div role="region" aria-label="Original Text">', unsafe_allow_html=True)
            st.markdown('<h5 tabindex="0">Original</h5>', unsafe_allow_html=True)
            st.text_area(
                "Original Text",
                value=st.session_state["original_text"],
                height=150,
                disabled=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div role="region" aria-label="Humanized Text">', unsafe_allow_html=True)
            st.markdown('<h5 tabindex="0">Humanized</h5>', unsafe_allow_html=True)
            st.text_area(
                "Humanized Text",
                value=st.session_state["humanized_text"],
                height=150,
                disabled=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_improvement_heatmap():
    """Render improvement heatmap with enhanced accessibility"""
    st.markdown('<div class="heatmap-container" role="region" aria-labelledby="heatmap-title">', unsafe_allow_html=True)
    st.markdown('<h4 id="heatmap-title" class="heatmap-title" tabindex="0">Improvement Areas</h4>', unsafe_allow_html=True)
    
    # Placeholder for the heatmap visualization
    st.info("This is a placeholder for the improvement heatmap visualization. In a real implementation, this would show a heatmap of areas that need improvement in the text.")
    
    st.markdown('</div>', unsafe_allow_html=True)
