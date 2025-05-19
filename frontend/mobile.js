/**
 * Humanyzer Mobile Experience Enhancements
 * This script improves the mobile experience and accessibility of the Humanyzer application.
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
  // Fix viewport height issues on mobile
  fixMobileViewportHeight();
  
  // Enhance keyboard navigation
  enhanceKeyboardNavigation();
  
  // Improve touch interactions
  improveTouchInteractions();
  
  // Add scroll-into-view for long forms
  addScrollIntoViewForForms();
  
  // Add swipe navigation for panels on mobile
  addSwipeNavigation();
  
  // Add ARIA attributes to improve accessibility
  enhanceAccessibility();
  
  // Add smooth transitions between states
  addSmoothTransitions();
  
  // Listen for window resize events
  window.addEventListener('resize', function() {
    fixMobileViewportHeight();
  });
});

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
}

/**
 * Enhance keyboard navigation for better accessibility
 */
function enhanceKeyboardNavigation() {
  // Add tabindex to interactive elements that might be missed
  const interactiveElements = document.querySelectorAll('.panel-title, .metric-card, .pattern-card');
  interactiveElements.forEach((element, index) => {
    if (!element.hasAttribute('tabindex')) {
      element.setAttribute('tabindex', '0');
    }
  });
  
  // Add keyboard event listeners for custom components
  document.addEventListener('keydown', function(event) {
    // Handle Enter key on custom interactive elements
    if (event.key === 'Enter') {
      const activeElement = document.activeElement;
      if (activeElement && activeElement.classList.contains('tone-option')) {
        activeElement.click();
      }
    }
    
    // Add Escape key handler for modals or expanded sections
    if (event.key === 'Escape') {
      const expandedSections = document.querySelectorAll('[aria-expanded="true"]');
      expandedSections.forEach(section => {
        if (section.hasAttribute('aria-controls')) {
          const controlId = section.getAttribute('aria-controls');
          const controlElement = document.getElementById(controlId);
          if (controlElement) {
            controlElement.style.display = 'none';
            section.setAttribute('aria-expanded', 'false');
          }
        }
      });
    }
  });
}

/**
 * Improve touch interactions for mobile devices
 */
function improveTouchInteractions() {
  // Increase touch target size for small buttons and controls
  const smallControls = document.querySelectorAll('.stButton button, .stCheckbox, .stRadio, .stSelectbox');
  smallControls.forEach(control => {
    control.style.minHeight = '44px';
    control.style.minWidth = '44px';
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
  
  // Fix double-tap issue on iOS
  document.addEventListener('touchend', function(event) {
    // Prevent zooming on double tap
    const now = Date.now();
    const DOUBLE_TAP_THRESHOLD = 300;
    
    if (lastTap && (now - lastTap) < DOUBLE_TAP_THRESHOLD) {
      event.preventDefault();
    }
    
    lastTap = now;
  }, { passive: false });
  
  // Variable to store the last tap time
  let lastTap = 0;
}

/**
 * Add scroll-into-view functionality for form elements
 */
function addScrollIntoViewForForms() {
  // Focus event for form inputs to scroll them into view on mobile
  const formInputs = document.querySelectorAll('input, textarea, select, [role="combobox"]');
  formInputs.forEach(input => {
    input.addEventListener('focus', function() {
      // Check if we're on a mobile device
      if (window.innerWidth <= 768) {
        // Scroll the element into view with smooth behavior
        setTimeout(() => {
          this.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
          });
        }, 300);
      }
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

/**
 * Add swipe navigation for panels on mobile
 */
function addSwipeNavigation() {
  // Only apply on mobile devices
  if (window.innerWidth > 768) return;
  
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
 * Enhance accessibility by adding ARIA attributes
 */
function enhanceAccessibility() {
  // Add ARIA labels to panels
  const inputPanel = document.querySelector('.input-panel');
  if (inputPanel) {
    inputPanel.setAttribute('role', 'region');
    inputPanel.setAttribute('aria-label', 'Input Panel');
  }
  
  const outputPanel = document.querySelector('.output-panel');
  if (outputPanel) {
    outputPanel.setAttribute('role', 'region');
    outputPanel.setAttribute('aria-label', 'Output Panel');
  }
  
  // Add ARIA labels to interactive elements
  const textAreas = document.querySelectorAll('textarea');
  textAreas.forEach(textarea => {
    if (!textarea.hasAttribute('aria-label')) {
      const label = textarea.previousElementSibling?.textContent || 'Text input';
      textarea.setAttribute('aria-label', label);
    }
  });
  
  // Add ARIA attributes to status indicators
  const statusIndicators = document.querySelectorAll('.status-indicator');
  statusIndicators.forEach(indicator => {
    indicator.setAttribute('role', 'status');
    indicator.setAttribute('aria-live', 'polite');
  });
  
  // Add ARIA attributes to analysis section
  const analysisSection = document.querySelector('.analysis-section');
  if (analysisSection) {
    analysisSection.setAttribute('role', 'region');
    analysisSection.setAttribute('aria-label', 'Analysis Results');
  }
  
  // Add ARIA attributes to quality metrics
  const qualityMetrics = document.querySelector('.quality-metrics-panel');
  if (qualityMetrics) {
    qualityMetrics.setAttribute('role', 'region');
    qualityMetrics.setAttribute('aria-label', 'Quality Metrics');
  }
  
  // Add ARIA attributes to loading indicators
  const loadingContainers = document.querySelectorAll('.loading-container');
  loadingContainers.forEach(container => {
    container.setAttribute('role', 'alert');
    container.setAttribute('aria-busy', 'true');
    container.setAttribute('aria-live', 'assertive');
  });
  
  // Add skip links for keyboard navigation
  addSkipLinks();
}

/**
 * Add skip links for keyboard navigation
 */
function addSkipLinks() {
  // Create skip links container
  const skipLinksContainer = document.createElement('div');
  skipLinksContainer.className = 'skip-links';
  skipLinksContainer.style.position = 'absolute';
  skipLinksContainer.style.top = '-1000px';
  skipLinksContainer.style.left = '0';
  skipLinksContainer.style.zIndex = '9999';
  skipLinksContainer.style.backgroundColor = 'var(--primary-color)';
  skipLinksContainer.style.padding = '10px';
  skipLinksContainer.style.transition = 'top 0.3s ease';
  
  // Create skip links
  const skipToInput = document.createElement('a');
  skipToInput.href = '#';
  skipToInput.textContent = 'Skip to input panel';
  skipToInput.style.color = 'white';
  skipToInput.style.display = 'block';
  skipToInput.style.padding = '5px';
  
  const skipToOutput = document.createElement('a');
  skipToOutput.href = '#';
  skipToOutput.textContent = 'Skip to output panel';
  skipToOutput.style.color = 'white';
  skipToOutput.style.display = 'block';
  skipToOutput.style.padding = '5px';
  
  // Add event listeners
  skipToInput.addEventListener('click', function(event) {
    event.preventDefault();
    const inputPanel = document.querySelector('.input-panel');
    if (inputPanel) {
      inputPanel.focus();
      inputPanel.scrollIntoView({ behavior: 'smooth' });
    }
  });
  
  skipToOutput.addEventListener('click', function(event) {
    event.preventDefault();
    const outputPanel = document.querySelector('.output-panel');
    if (outputPanel) {
      outputPanel.focus();
      outputPanel.scrollIntoView({ behavior: 'smooth' });
    }
  });
  
  // Show skip links on focus
  skipToInput.addEventListener('focus', function() {
    skipLinksContainer.style.top = '0';
  });
  
  skipToOutput.addEventListener('focus', function() {
    skipLinksContainer.style.top = '0';
  });
  
  // Hide skip links on blur
  skipToInput.addEventListener('blur', function() {
    skipLinksContainer.style.top = '-1000px';
  });
  
  skipToOutput.addEventListener('blur', function() {
    skipLinksContainer.style.top = '-1000px';
  });
  
  // Add skip links to container
  skipLinksContainer.appendChild(skipToInput);
  skipLinksContainer.appendChild(skipToOutput);
  
  // Add container to document
  document.body.insertBefore(skipLinksContainer, document.body.firstChild);
}

/**
 * Add smooth transitions between states
 */
function addSmoothTransitions() {
  // Add transition class to elements that should animate
  const transitionElements = document.querySelectorAll(
    '.workspace-container, .input-panel, .output-panel, .panel-title, ' +
    '.loading-container, .results-display, .quality-metrics-panel, ' +
    '.analysis-section, .text-comparison, .pattern-card, .suggestion-card'
  );
  
  transitionElements.forEach(element => {
    element.classList.add('transition-element');
  });
  
  // Add CSS for transition elements if not already in stylesheet
  if (!document.querySelector('#transition-styles')) {
    const styleElement = document.createElement('style');
    styleElement.id = 'transition-styles';
    styleElement.textContent = `
      .transition-element {
        transition: all 0.3s ease;
      }
      
      .fade-in {
        animation: fadeIn 0.5s ease-out;
      }
      
      @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      .touch-active {
        transform: scale(0.98);
        opacity: 0.9;
      }
    `;
    
    document.head.appendChild(styleElement);
  }
  
  // Add fade-in animation to dynamically loaded content
  const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      if (mutation.addedNodes) {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === 1 && (
              node.classList.contains('results-display') ||
              node.classList.contains('quality-metrics-panel') ||
              node.classList.contains('analysis-section') ||
              node.classList.contains('text-comparison') ||
              node.classList.contains('pattern-card') ||
              node.classList.contains('suggestion-card')
          )) {
            node.classList.add('fade-in');
          }
        });
      }
    });
  });
  
  // Start observing the document body for added nodes
  observer.observe(document.body, { childList: true, subtree: true });
}
