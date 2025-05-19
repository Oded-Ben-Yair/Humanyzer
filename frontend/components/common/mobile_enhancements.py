"""
Mobile Enhancements Component for Humanyzer
This component improves the mobile experience with touch-friendly interactions and responsive adjustments.
"""
import streamlit as st
import streamlit.components.v1 as components

def render_mobile_enhancements():
    """
    Render a hidden component that enhances the mobile experience.
    This improves touch interactions, fixes viewport issues, and adds mobile-specific features.
    """
    # Custom HTML/JS component for mobile enhancements
    mobile_enhancements_html = """
    <div id="mobile-enhancements-component" style="display: none;"></div>

    <script>
    (function() {
        // Detect if we're on a mobile device
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth < 768;
        
        if (isMobile) {
            // Fix viewport height issues on mobile browsers
            fixMobileViewportHeight();
            
            // Improve touch targets
            improveTouchTargets();
            
            // Add swipe navigation for panels
            addSwipeNavigation();
            
            // Fix double-tap issues
            fixDoubleTapIssues();
            
            // Add mobile-specific UI adjustments
            addMobileUIAdjustments();
            
            // Add scroll-into-view for form elements
            addScrollIntoViewForForms();
            
            // Listen for orientation changes
            window.addEventListener('orientationchange', function() {
                setTimeout(fixMobileViewportHeight, 300);
                setTimeout(improveTouchTargets, 300);
            });
            
            // Listen for resize events
            window.addEventListener('resize', function() {
                fixMobileViewportHeight();
            });
        }
        
        /**
         * Fix viewport height issues on mobile browsers
         * This addresses the issue with 100vh not accounting for browser UI on mobile
         */
        function fixMobileViewportHeight() {
            // Get the viewport height
            const vh = window.innerHeight * 0.01;
            
            // Set the --vh custom property to the root of the document
            document.documentElement.style.setProperty('--vh', `${vh}px`);
            
            // Apply the custom height to relevant containers
            const workspaceContainers = document.querySelectorAll('.workspace-container');
            workspaceContainers.forEach(container => {
                container.style.minHeight = `calc(var(--vh, 1vh) * 80)`;
            });
            
            // Fix for iOS Safari bouncing scroll effect
            document.body.style.overscrollBehavior = 'none';
            
            // Adjust panels for mobile view
            const panels = document.querySelectorAll('.input-panel, .output-panel');
            panels.forEach(panel => {
                panel.style.width = '100%';
                panel.style.maxWidth = '100%';
                panel.style.marginBottom = '1.5rem';
            });
        }
        
        /**
         * Improve touch targets for better mobile interaction
         */
        function improveTouchTargets() {
            // Increase touch target size for small buttons and controls
            const smallControls = document.querySelectorAll('.stButton button, .stCheckbox, .stRadio, .stSelectbox');
            smallControls.forEach(control => {
                control.style.minHeight = '44px';
                control.style.minWidth = '44px';
                control.style.padding = '10px 16px';
            });
            
            // Improve form elements spacing
            const formElements = document.querySelectorAll('.stTextInput input, .stSelectbox > div, .stNumberInput input');
            formElements.forEach(element => {
                element.style.minHeight = '44px';
                element.style.marginBottom = '0.75rem';
            });
            
            // Add active state for touch feedback
            const interactiveElements = document.querySelectorAll('.stButton button, .tone-option, .pattern-card, .suggestion-card');
            interactiveElements.forEach(element => {
                element.addEventListener('touchstart', function() {
                    this.classList.add('touch-active');
                });
                
                element.addEventListener('touchend', function() {
                    this.classList.remove('touch-active');
                });
                
                element.addEventListener('touchcancel', function() {
                    this.classList.remove('touch-active');
                });
            });
            
            // Add CSS for touch active state
            const style = document.createElement('style');
            style.textContent = `
                .touch-active {
                    transform: scale(0.98) !important;
                    opacity: 0.9 !important;
                    transition: transform 0.1s ease, opacity 0.1s ease !important;
                }
            `;
            document.head.appendChild(style);
        }
        
        /**
         * Add swipe navigation for panels on mobile
         */
        function addSwipeNavigation() {
            let touchStartX = 0;
            let touchEndX = 0;
            
            // Get the workspace container
            const workspaceContainer = document.querySelector('.workspace-container');
            if (!workspaceContainer) return;
            
            // Add touch event listeners
            workspaceContainer.addEventListener('touchstart', function(event) {
                touchStartX = event.changedTouches[0].screenX;
            }, { passive: true });
            
            workspaceContainer.addEventListener('touchend', function(event) {
                touchEndX = event.changedTouches[0].screenX;
                handleSwipe();
            }, { passive: true });
            
            // Handle the swipe gesture
            function handleSwipe() {
                const SWIPE_THRESHOLD = 100;
                const panels = workspaceContainer.querySelectorAll('.input-panel, .output-panel');
                
                if (panels.length < 2) return;
                
                // Left swipe (input to output)
                if (touchEndX < touchStartX - SWIPE_THRESHOLD) {
                    // Hide input panel, show output panel
                    panels[0].style.display = 'none';
                    panels[1].style.display = 'block';
                    
                    // Add a back button
                    addBackButton(panels[1], 'Back to Input');
                }
                
                // Right swipe (output to input)
                if (touchEndX > touchStartX + SWIPE_THRESHOLD) {
                    // Hide output panel, show input panel
                    panels[1].style.display = 'none';
                    panels[0].style.display = 'block';
                    
                    // Add a forward button
                    addBackButton(panels[0], 'View Results');
                }
            }
            
            // Add a back/forward button to navigate between panels
            function addBackButton(panel, text) {
                // Remove any existing back buttons
                const existingButtons = panel.querySelectorAll('.panel-nav-button');
                existingButtons.forEach(button => button.remove());
                
                // Create a new button
                const button = document.createElement('button');
                button.textContent = text;
                button.className = 'panel-nav-button';
                button.setAttribute('aria-label', text);
                
                // Style the button
                button.style.position = 'sticky';
                button.style.top = '10px';
                button.style.zIndex = '100';
                button.style.padding = '8px 16px';
                button.style.backgroundColor = 'var(--primary-color)';
                button.style.color = 'white';
                button.style.border = 'none';
                button.style.borderRadius = '4px';
                button.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
                button.style.margin = '0 0 10px 0';
                
                // Add click event
                button.addEventListener('click', function() {
                    const panels = document.querySelectorAll('.input-panel, .output-panel');
                    panels.forEach(p => {
                        p.style.display = p === panel ? 'none' : 'block';
                    });
                    
                    // Add a new back button to the other panel
                    const otherPanel = panel === panels[0] ? panels[1] : panels[0];
                    const otherText = text === 'Back to Input' ? 'View Results' : 'Back to Input';
                    addBackButton(otherPanel, otherText);
                });
                
                // Add the button to the panel
                panel.insertBefore(button, panel.firstChild);
            }
        }
        
        /**
         * Fix double-tap issues on iOS
         */
        function fixDoubleTapIssues() {
            // Prevent zooming on double tap
            let lastTap = 0;
            document.addEventListener('touchend', function(event) {
                const now = Date.now();
                const DOUBLE_TAP_THRESHOLD = 300;
                
                if (lastTap && (now - lastTap) < DOUBLE_TAP_THRESHOLD) {
                    event.preventDefault();
                }
                
                lastTap = now;
            }, { passive: false });
            
            // Add CSS to prevent text selection on double tap
            const style = document.createElement('style');
            style.textContent = `
                .stButton button, .tone-option, .pattern-card, .suggestion-card, .panel-title, .status-indicator {
                    -webkit-touch-callout: none;
                    -webkit-user-select: none;
                    user-select: none;
                }
            `;
            document.head.appendChild(style);
        }
        
        /**
         * Add mobile-specific UI adjustments
         */
        function addMobileUIAdjustments() {
            // Add CSS for mobile-specific adjustments
            const style = document.createElement('style');
            style.textContent = `
                @media (max-width: 768px) {
                    /* Stack columns on mobile */
                    .row-widget.stHorizontal {
                        flex-direction: column;
                    }
                    
                    .row-widget.stHorizontal > div {
                        width: 100% !important;
                        margin-right: 0 !important;
                        margin-bottom: 1rem;
                    }
                    
                    /* Adjust text sizes for better readability */
                    .panel-title {
                        font-size: 1.1rem;
                    }
                    
                    h4 {
                        font-size: 1rem;
                    }
                    
                    /* Ensure text areas are properly sized */
                    .stTextArea textarea {
                        min-height: 200px;
                        font-size: 16px !important; /* Prevent iOS zoom on focus */
                    }
                    
                    /* Improve button touch targets */
                    .stButton > button {
                        min-height: 48px;
                        width: 100%;
                    }
                    
                    /* Adjust metrics display */
                    .quality-metrics {
                        flex-direction: column;
                    }
                    
                    .metric-card {
                        margin-bottom: 0.75rem;
                    }
                    
                    /* Fix for iOS input zoom */
                    input, select, textarea {
                        font-size: 16px !important;
                    }
                    
                    /* Add bottom padding to prevent content from being hidden behind fixed elements */
                    body {
                        padding-bottom: 60px;
                    }
                }
            `;
            document.head.appendChild(style);
            
            // Add a floating action button for quick actions
            addFloatingActionButton();
        }
        
        /**
         * Add a floating action button for quick mobile actions
         */
        function addFloatingActionButton() {
            // Create the floating action button
            const fab = document.createElement('button');
            fab.className = 'mobile-fab';
            fab.setAttribute('aria-label', 'Quick actions');
            fab.innerHTML = '<span>+</span>';
            
            // Style the button
            fab.style.position = 'fixed';
            fab.style.bottom = '20px';
            fab.style.right = '20px';
            fab.style.width = '56px';
            fab.style.height = '56px';
            fab.style.borderRadius = '50%';
            fab.style.backgroundColor = 'var(--primary-color)';
            fab.style.color = 'white';
            fab.style.border = 'none';
            fab.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.2)';
            fab.style.zIndex = '1000';
            fab.style.fontSize = '24px';
            fab.style.display = 'flex';
            fab.style.alignItems = 'center';
            fab.style.justifyContent = 'center';
            fab.style.transition = 'all 0.3s ease';
            
            // Create the menu container
            const fabMenu = document.createElement('div');
            fabMenu.className = 'mobile-fab-menu';
            fabMenu.style.position = 'fixed';
            fabMenu.style.bottom = '80px';
            fabMenu.style.right = '20px';
            fabMenu.style.display = 'none';
            fabMenu.style.flexDirection = 'column';
            fabMenu.style.gap = '10px';
            fabMenu.style.zIndex = '999';
            
            // Add menu items
            const menuItems = [
                { text: 'Transform', icon: '🔄', action: () => clickTransformButton() },
                { text: 'Copy', icon: '📋', action: () => clickCopyButton() },
                { text: 'Help', icon: '❓', action: () => showMobileHelp() }
            ];
            
            menuItems.forEach(item => {
                const menuItem = document.createElement('button');
                menuItem.className = 'mobile-fab-menu-item';
                menuItem.innerHTML = `<span>${item.icon}</span><span>${item.text}</span>`;
                
                // Style the menu item
                menuItem.style.display = 'flex';
                menuItem.style.alignItems = 'center';
                menuItem.style.gap = '8px';
                menuItem.style.backgroundColor = 'white';
                menuItem.style.color = 'var(--primary-color)';
                menuItem.style.border = 'none';
                menuItem.style.borderRadius = '20px';
                menuItem.style.padding = '8px 16px';
                menuItem.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.1)';
                menuItem.style.transition = 'all 0.2s ease';
                
                // Add hover effect
                menuItem.addEventListener('mouseover', function() {
                    this.style.transform = 'translateX(-5px)';
                    this.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.15)';
                });
                
                menuItem.addEventListener('mouseout', function() {
                    this.style.transform = 'translateX(0)';
                    this.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.1)';
                });
                
                // Add click event
                menuItem.addEventListener('click', function() {
                    // Close the menu
                    fabMenu.style.display = 'none';
                    fab.classList.remove('active');
                    
                    // Execute the action
                    item.action();
                });
                
                fabMenu.appendChild(menuItem);
            });
            
            // Add click event to toggle the menu
            fab.addEventListener('click', function() {
                if (fabMenu.style.display === 'none') {
                    fabMenu.style.display = 'flex';
                    this.classList.add('active');
                    this.innerHTML = '<span>×</span>';
                } else {
                    fabMenu.style.display = 'none';
                    this.classList.remove('active');
                    this.innerHTML = '<span>+</span>';
                }
            });
            
            // Add the elements to the document
            document.body.appendChild(fab);
            document.body.appendChild(fabMenu);
            
            // Helper functions for menu actions
            function clickTransformButton() {
                const transformButton = document.querySelector('button:contains("Humanize Text"), button:contains("Transform Text")');
                if (transformButton) {
                    transformButton.click();
                }
            }
            
            function clickCopyButton() {
                const copyButton = document.querySelector('button:contains("Copy Humanized Text")');
                if (copyButton) {
                    copyButton.click();
                }
            }
            
            function showMobileHelp() {
                // Create a help dialog
                const helpDialog = document.createElement('div');
                helpDialog.className = 'mobile-help-dialog';
                helpDialog.style.position = 'fixed';
                helpDialog.style.top = '0';
                helpDialog.style.left = '0';
                helpDialog.style.width = '100%';
                helpDialog.style.height = '100%';
                helpDialog.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
                helpDialog.style.zIndex = '2000';
                helpDialog.style.display = 'flex';
                helpDialog.style.alignItems = 'center';
                helpDialog.style.justifyContent = 'center';
                
                // Create the dialog content
                const dialogContent = document.createElement('div');
                dialogContent.className = 'mobile-help-content';
                dialogContent.style.backgroundColor = 'white';
                dialogContent.style.borderRadius = '8px';
                dialogContent.style.padding = '20px';
                dialogContent.style.maxWidth = '90%';
                dialogContent.style.maxHeight = '80%';
                dialogContent.style.overflow = 'auto';
                dialogContent.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)';
                
                dialogContent.innerHTML = `
                    <h3 style="color: var(--primary-color); margin-top: 0;">Mobile Tips</h3>
                    <ul style="padding-left: 20px; margin-bottom: 20px;">
                        <li><strong>Swipe</strong> between input and output panels</li>
                        <li>Use the <strong>+</strong> button for quick actions</li>
                        <li><strong>Tap and hold</strong> text to select and copy</li>
                        <li>Rotate your device for a better view</li>
                        <li>Use the <strong>Copy</strong> button to easily copy results</li>
                    </ul>
                    <button id="close-help-dialog" style="background-color: var(--primary-color); color: white; border: none; padding: 8px 16px; border-radius: 4px; width: 100%;">Close</button>
                `;
                
                helpDialog.appendChild(dialogContent);
                document.body.appendChild(helpDialog);
                
                // Add close button event
                document.getElementById('close-help-dialog').addEventListener('click', function() {
                    document.body.removeChild(helpDialog);
                });
                
                // Close dialog when clicking outside
                helpDialog.addEventListener('click', function(event) {
                    if (event.target === helpDialog) {
                        document.body.removeChild(helpDialog);
                    }
                });
            }
        }
        
        /**
         * Add scroll-into-view functionality for form elements
         */
        function addScrollIntoViewForForms() {
            // Focus event for form inputs to scroll them into view on mobile
            const formInputs = document.querySelectorAll('input, textarea, select, [role="combobox"]');
            formInputs.forEach(input => {
                input.addEventListener('focus', function() {
                    // Scroll the element into view with smooth behavior
                    setTimeout(() => {
                        this.scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }, 300);
                });
            });
            
            // Add scroll into view for validation messages
            const observer = new MutationObserver(mutations => {
                mutations.forEach(mutation => {
                    if (mutation.addedNodes) {
                        mutation.addedNodes.forEach(node => {
                            // Check if the added node is an error message
                            if (node.nodeType === 1 && (
                                node.classList.contains('stAlert') || 
                                node.textContent.includes('Error') || 
                                node.textContent.includes('Invalid')
                            )) {
                                node.scrollIntoView({
                                    behavior: 'smooth',
                                    block: 'center'
                                });
                            }
                        });
                    }
                });
            });
            
            // Start observing the document body for added nodes
            observer.observe(document.body, { childList: true, subtree: true });
        }
    })();
    </script>
    """
    
    # Render the component with a height of 0 to make it invisible
    components.html(mobile_enhancements_html, height=0)

def add_mobile_enhancements_to_page():
    """
    Add mobile enhancements to the current page.
    This function should be called at the beginning of each page.
    """
    render_mobile_enhancements()
