
"""
Humanyzer Text Comparison
This file implements the before/after text comparison with highlighted changes.
"""
import streamlit as st
import difflib

def render_text_comparison(original_text, humanized_text):
    """Render before/after text comparison with highlighted changes"""
    if not original_text or not humanized_text:
        return
    
    st.markdown('<div class="text-comparison-container">', unsafe_allow_html=True)
    st.markdown('<h4>Before/After Comparison</h4>', unsafe_allow_html=True)
    
    # Generate diff
    diff_html = generate_diff_html(original_text, humanized_text)
    
    # Display diff
    st.markdown(
        f"""
        <div class="diff-display">
            {diff_html}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

def generate_diff_html(text1, text2):
    """Generate HTML diff between two texts"""
    # Split texts into words
    words1 = text1.split()
    words2 = text2.split()
    
    # Generate diff
    d = difflib.Differ()
    diff = list(d.compare(words1, words2))
    
    # Convert diff to HTML
    html = []
    for word in diff:
        if word.startswith('+ '):
            html.append(f'<span class="diff-added">{word[2:]}</span>')
        elif word.startswith('- '):
            html.append(f'<span class="diff-removed">{word[2:]}</span>')
        elif word.startswith('  '):
            html.append(word[2:])
    
    return ' '.join(html)
