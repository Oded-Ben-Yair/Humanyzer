"""
Keyboard Navigation Component for Humanyzer
This component enhances keyboard navigation and accessibility across the application.
"""
import streamlit as st
import streamlit.components.v1 as components

def render_keyboard_nav():
    """
    Render a hidden component that enhances keyboard navigation.
    This adds skip links and improves focus management for keyboard users.
    """
    # Custom HTML/JS component for keyboard navigation
    keyboard_nav_html = """
    <div id="keyboard-nav-component" style="display: none;">
        <!-- Skip links for keyboard navigation -->
        <div class="skip-links" style="position: absolute; top: -1000px; left: 0; z-index: 9999;">
            <a href="#workspace-title" id="skip-to-content" style="background-color: #5B21B6; color: white; padding: 10px; display: block;">Skip to content</a>
            <a href="#input-panel-title" id="skip-to-input" style="background-color: #5B21B6; color: white; padding: 10px; display: block;">Skip to input panel</a>
            <a href="#output-panel-title" id="skip-to-output" style="background-color: #5B21B6; color: white; padding: 10px; display: block;">Skip to output panel</a>
        </div>
    </div>

    <script>
    (function() {
        // Show skip links when they receive focus
        const skipLinks = document.querySelectorAll('.skip-links a');
        skipLinks.forEach(link => {
            link.addEventListener('focus', function() {
                this.style.position = 'fixed';
                this.style.top = '10px';
                this.style.left = '10px';
            });
            
            link.addEventListener('blur', function() {
                this.style.position = 'absolute';
                this.style.top = '-1000px';
                this.style.left = '0';
            });
        });
        
        // Add keyboard shortcut support
        document.addEventListener('keydown', function(event) {
            // Alt+1: Skip to content
            if (event.altKey && event.key === '1') {
                event.preventDefault();
                const contentElement = document.getElementById('workspace-title');
                if (contentElement) {
                    contentElement.focus();
                    contentElement.scrollIntoView({ behavior: 'smooth' });
                }
            }
            
            // Alt+2: Skip to input panel
            if (event.altKey && event.key === '2') {
                event.preventDefault();
                const inputPanel = document.getElementById('input-panel-title');
                if (inputPanel) {
                    inputPanel.focus();
                    inputPanel.scrollIntoView({ behavior: 'smooth' });
                }
            }
            
            // Alt+3: Skip to output panel
            if (event.altKey && event.key === '3') {
                event.preventDefault();
                const outputPanel = document.getElementById('output-panel-title');
                if (outputPanel) {
                    outputPanel.focus();
                    outputPanel.scrollIntoView({ behavior: 'smooth' });
                }
            }
            
            // Escape key: Close any open dialogs or return focus to main content
            if (event.key === 'Escape') {
                const expandedElements = document.querySelectorAll('[aria-expanded="true"]');
                expandedElements.forEach(element => {
                    if (element.hasAttribute('aria-controls')) {
                        const controlId = element.getAttribute('aria-controls');
                        const controlElement = document.getElementById(controlId);
                        if (controlElement) {
                            element.setAttribute('aria-expanded', 'false');
                            controlElement.style.display = 'none';
                        }
                    }
                });
            }
        });
        
        // Enhance focus visibility
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Tab') {
                document.body.classList.add('keyboard-user');
            }
        });
        
        document.addEventListener('mousedown', function() {
            document.body.classList.remove('keyboard-user');
        });
        
        // Add CSS for enhanced focus visibility
        const style = document.createElement('style');
        style.textContent = `
            .keyboard-user *:focus {
                outline: 3px solid #5B21B6 !important;
                outline-offset: 2px !important;
                box-shadow: 0 0 0 4px rgba(91, 33, 182, 0.3) !important;
            }
            
            .keyboard-user .stButton button:focus {
                outline: 3px solid #5B21B6 !important;
                outline-offset: 2px !important;
                box-shadow: 0 0 0 4px rgba(91, 33, 182, 0.3) !important;
            }
            
            .keyboard-user .stTextArea textarea:focus {
                outline: 3px solid #5B21B6 !important;
                outline-offset: 2px !important;
                box-shadow: 0 0 0 4px rgba(91, 33, 182, 0.3) !important;
            }
            
            .keyboard-user .stSelectbox [data-baseweb="select"]:focus-within {
                outline: 3px solid #5B21B6 !important;
                outline-offset: 2px !important;
                box-shadow: 0 0 0 4px rgba(91, 33, 182, 0.3) !important;
            }
        `;
        document.head.appendChild(style);
        
        // Add keyboard instructions
        const keyboardInstructions = document.createElement('div');
        keyboardInstructions.className = 'keyboard-instructions';
        keyboardInstructions.setAttribute('role', 'region');
        keyboardInstructions.setAttribute('aria-label', 'Keyboard Navigation Instructions');
        keyboardInstructions.style.display = 'none';
        keyboardInstructions.style.position = 'fixed';
        keyboardInstructions.style.bottom = '20px';
        keyboardInstructions.style.right = '20px';
        keyboardInstructions.style.backgroundColor = 'white';
        keyboardInstructions.style.padding = '15px';
        keyboardInstructions.style.borderRadius = '8px';
        keyboardInstructions.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        keyboardInstructions.style.zIndex = '1000';
        keyboardInstructions.style.maxWidth = '300px';
        
        keyboardInstructions.innerHTML = `
            <h3 style="margin-top: 0; color: #5B21B6;">Keyboard Shortcuts</h3>
            <ul style="padding-left: 20px; margin-bottom: 10px;">
                <li><strong>Alt + 1:</strong> Skip to main content</li>
                <li><strong>Alt + 2:</strong> Skip to input panel</li>
                <li><strong>Alt + 3:</strong> Skip to output panel</li>
                <li><strong>Tab:</strong> Navigate between elements</li>
                <li><strong>Shift + Tab:</strong> Navigate backwards</li>
                <li><strong>Enter/Space:</strong> Activate buttons</li>
                <li><strong>Escape:</strong> Close dialogs</li>
            </ul>
            <button id="close-keyboard-instructions" style="background-color: #5B21B6; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">Close</button>
        `;
        
        document.body.appendChild(keyboardInstructions);
        
        // Show keyboard instructions when pressing ?
        document.addEventListener('keydown', function(event) {
            if (event.key === '?' || (event.shiftKey && event.key === '/')) {
                event.preventDefault();
                keyboardInstructions.style.display = 'block';
            }
        });
        
        // Close button for keyboard instructions
        document.getElementById('close-keyboard-instructions').addEventListener('click', function() {
            keyboardInstructions.style.display = 'none';
        });
        
        // Close keyboard instructions with Escape
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && keyboardInstructions.style.display === 'block') {
                keyboardInstructions.style.display = 'none';
            }
        });
        
        // Add a small keyboard help button
        const keyboardHelpButton = document.createElement('button');
        keyboardHelpButton.textContent = '⌨️';
        keyboardHelpButton.setAttribute('aria-label', 'Keyboard navigation help');
        keyboardHelpButton.style.position = 'fixed';
        keyboardHelpButton.style.bottom = '20px';
        keyboardHelpButton.style.right = '20px';
        keyboardHelpButton.style.backgroundColor = '#5B21B6';
        keyboardHelpButton.style.color = 'white';
        keyboardHelpButton.style.border = 'none';
        keyboardHelpButton.style.borderRadius = '50%';
        keyboardHelpButton.style.width = '40px';
        keyboardHelpButton.style.height = '40px';
        keyboardHelpButton.style.fontSize = '20px';
        keyboardHelpButton.style.cursor = 'pointer';
        keyboardHelpButton.style.zIndex = '999';
        keyboardHelpButton.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.2)';
        
        keyboardHelpButton.addEventListener('click', function() {
            keyboardInstructions.style.display = 'block';
        });
        
        document.body.appendChild(keyboardHelpButton);
    })();
    </script>
    """
    
    # Render the component with a height of 0 to make it invisible
    components.html(keyboard_nav_html, height=0)

def add_keyboard_nav_to_page():
    """
    Add keyboard navigation to the current page.
    This function should be called at the beginning of each page.
    """
    render_keyboard_nav()
