"""
Transitions Component for Humanyzer
This component adds smooth transitions between states and enhances the UI experience.
"""
import streamlit as st
import streamlit.components.v1 as components

def render_transitions():
    """
    Render a hidden component that adds smooth transitions between states.
    This improves the user experience by making state changes less jarring.
    """
    # Custom HTML/JS component for transitions
    transitions_html = """
    <div id="transitions-component" style="display: none;"></div>

    <script>
    (function() {
        // Add CSS for transitions
        const style = document.createElement('style');
        style.textContent = `
            /* Base transitions for all elements */
            .streamlit-container * {
                transition: all 0.3s ease;
            }
            
            /* Fade-in animation */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            /* Fade-out animation */
            @keyframes fadeOut {
                from { opacity: 1; transform: translateY(0); }
                to { opacity: 0; transform: translateY(10px); }
            }
            
            /* Slide-in animation */
            @keyframes slideIn {
                from { transform: translateX(-20px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            /* Pulse animation for loading states */
            @keyframes pulse {
                0% { opacity: 0.6; }
                50% { opacity: 1; }
                100% { opacity: 0.6; }
            }
            
            /* Apply animations to specific elements */
            .input-panel, .output-panel {
                animation: slideIn 0.4s ease-out;
            }
            
            .results-display, .quality-metrics-panel, .analysis-section {
                animation: fadeIn 0.5s ease-out;
            }
            
            .loading-container {
                animation: pulse 1.5s infinite;
            }
            
            /* Hover transitions */
            .stButton > button {
                transition: all 0.2s ease !important;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 8px rgba(98, 0, 234, 0.3) !important;
            }
            
            .stButton > button:active {
                transform: translateY(0) !important;
                box-shadow: 0 1px 2px rgba(98, 0, 234, 0.2) !important;
            }
            
            /* Panel transitions */
            .panel-title, .quality-metrics-title, .analysis-title {
                position: relative;
                overflow: hidden;
            }
            
            .panel-title::after, .quality-metrics-title::after, .analysis-title::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 2px;
                background-color: var(--primary-light);
                transform: scaleX(0);
                transform-origin: bottom right;
                transition: transform 0.3s ease;
            }
            
            .panel-title:hover::after, .quality-metrics-title:hover::after, .analysis-title:hover::after {
                transform: scaleX(1);
                transform-origin: bottom left;
            }
            
            /* Card hover effects */
            .metric-card, .pattern-card, .suggestion-card, .profile-card {
                transition: all 0.3s ease;
            }
            
            .metric-card:hover, .pattern-card:hover, .suggestion-card:hover, .profile-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
            }
            
            /* Status indicator transitions */
            .status-indicator {
                transition: all 0.3s ease;
            }
            
            .status-indicator:hover {
                transform: translateY(-2px);
            }
            
            .status-indicator-dot {
                transition: all 0.3s ease;
            }
            
            .status-indicator:hover .status-indicator-dot {
                transform: scale(1.2);
            }
            
            /* Text area focus transition */
            .stTextArea textarea {
                transition: all 0.3s ease;
            }
            
            .stTextArea textarea:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 2px rgba(98, 0, 234, 0.2);
            }
        `;
        document.head.appendChild(style);
        
        // Add transition classes to elements when they appear
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                if (mutation.addedNodes) {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1) { // Element node
                            // Add transition classes based on element type
                            if (node.classList.contains('stButton')) {
                                node.classList.add('transition-element');
                            }
                            
                            // Find and add transitions to specific elements
                            const panels = node.querySelectorAll('.input-panel, .output-panel');
                            panels.forEach(panel => panel.classList.add('transition-element'));
                            
                            const results = node.querySelectorAll('.results-display, .quality-metrics-panel, .analysis-section');
                            results.forEach(result => result.classList.add('transition-element'));
                            
                            const cards = node.querySelectorAll('.metric-card, .pattern-card, .suggestion-card, .profile-card');
                            cards.forEach(card => card.classList.add('transition-element'));
                            
                            const indicators = node.querySelectorAll('.status-indicator');
                            indicators.forEach(indicator => indicator.classList.add('transition-element'));
                        }
                    });
                }
            });
        });
        
        // Start observing the document body for added nodes
        observer.observe(document.body, { childList: true, subtree: true });
        
        // Add smooth page transitions
        let lastUrl = location.href; 
        
        // Create a MutationObserver to detect URL changes (for Streamlit navigation)
        const urlObserver = new MutationObserver(() => {
            const url = location.href;
            if (url !== lastUrl) {
                lastUrl = url;
                
                // Add a transition effect when the URL changes
                const mainContent = document.querySelector('.main');
                if (mainContent) {
                    mainContent.style.opacity = '0';
                    mainContent.style.transform = 'translateY(10px)';
                    
                    setTimeout(() => {
                        mainContent.style.opacity = '1';
                        mainContent.style.transform = 'translateY(0)';
                    }, 100);
                }
            }
        });
        
        // Start observing the document body for URL changes
        urlObserver.observe(document.body, { childList: true, subtree: true });
        
        // Add transition when clicking buttons
        document.addEventListener('click', function(event) {
            if (event.target.tagName === 'BUTTON' || 
                event.target.closest('button') || 
                event.target.classList.contains('stButton')) {
                
                // Find the main content area
                const mainContent = document.querySelector('.main');
                if (mainContent) {
                    // Add a subtle pulse effect
                    mainContent.style.transition = 'all 0.2s ease';
                    mainContent.style.transform = 'scale(0.99)';
                    
                    setTimeout(() => {
                        mainContent.style.transform = 'scale(1)';
                    }, 200);
                }
            }
        });
    })();
    </script>
    """
    
    # Render the component with a height of 0 to make it invisible
    components.html(transitions_html, height=0)

def add_transitions_to_page():
    """
    Add smooth transitions to the current page.
    This function should be called at the beginning of each page.
    """
    render_transitions()
