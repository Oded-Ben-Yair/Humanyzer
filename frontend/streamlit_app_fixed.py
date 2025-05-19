"""
Humanyze - Make AI Sound Like You
Main Streamlit application entry point
"""
import streamlit as st
import os
import sys
from streamlit.web.cli import main as stcli

def main():
    # Set up the Streamlit application
    st.set_page_config(
        page_title="Humanyze - Make AI Sound Like You",
        page_icon="🔄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Header
    st.markdown(
        """
        <div class="header">
            <h1>Humanyze</h1>
            <h3>Make AI Sound Like You</h3>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["Transform Content", "Analysis Results", "About"])
    
    with tab1:
        st.header("Transform Your AI-Generated Content")
        
        # Check if user is logged in
        from auth import is_authenticated
        if not is_authenticated():
            st.warning("Please log in to use this feature.")
            st.info("Use the login button in the sidebar to access your account.")
        else:
            st.write("Enter your AI-generated text below to transform it to match your writing style.")
            
            # Text input area
            user_text = st.text_area("AI-generated text:", height=200)
            
            col1, col2 = st.columns([1, 3])
            with col1:
                # Style selection
                st.subheader("Style Options")
                style_profile = st.selectbox(
                    "Select your style profile:",
                    ["Professional", "Casual", "Academic", "Creative", "Custom"]
                )
                
                if style_profile == "Custom":
                    st.info("Custom profiles can be created in the Style Profiles section.")
                
                # Transformation options
                st.subheader("Transformation Options")
                preserve_meaning = st.slider("Preserve Original Meaning", 0, 100, 80)
                style_strength = st.slider("Style Strength", 0, 100, 70)
                
                # Advanced options
                with st.expander("Advanced Options"):
                    sentence_variety = st.checkbox("Enhance sentence variety", value=True)
                    vocabulary_richness = st.checkbox("Enhance vocabulary richness", value=True)
                    transition_words = st.checkbox("Add transition words", value=True)
            
            with col2:
                if user_text:
                    if st.button("Transform Text"):
                        with st.spinner("Transforming your text..."):
                            # Simulate processing time
                            import time
                            time.sleep(2)
                            
                            # This would be replaced with actual API call in production
                            transformed_text = f"[Transformed with {style_profile} style, {preserve_meaning}% meaning preservation, and {style_strength}% style strength]\n\n{user_text}"
                            
                            st.success("Text transformed successfully!")
                            st.text_area("Transformed text:", transformed_text, height=300)
                            
                            # Download option
                            st.download_button(
                                "Download transformed text",
                                transformed_text,
                                "transformed_text.txt",
                                "text/plain"
                            )
                else:
                    st.info("Enter some text to transform it according to your style preferences.")
    
    with tab2:
        st.header("Analysis Results")
        
        if not is_authenticated():
            st.warning("Please log in to view analysis results.")
        else:
            st.info("This section will show analytics and insights about your writing style and transformations.")
            
            # Placeholder for analytics
            st.subheader("Your Writing Style Profile")
            
            import random
            metrics = {
                "Sentence Length": random.randint(10, 25),
                "Vocabulary Diversity": random.randint(60, 95),
                "Formality Score": random.randint(30, 90),
                "Readability": random.randint(50, 95)
            }
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Avg. Sentence Length", f"{metrics['Sentence Length']} words")
            col2.metric("Vocabulary Diversity", f"{metrics['Vocabulary Diversity']}%")
            col3.metric("Formality Score", f"{metrics['Formality Score']}/100")
            col4.metric("Readability", f"{metrics['Readability']}/100")
            
            st.subheader("Recent Transformations")
            st.info("Your recent text transformations will appear here.")
            
            # Placeholder for transformation history
            st.write("No recent transformations found.")
    
    with tab3:
        st.header("About Humanyze")
        
        st.markdown("""
        ### Make AI Sound Like You
        
        Humanyze is an advanced tool that helps you transform AI-generated content to match your unique writing style.
        
        #### Key Features:
        
        - **Style Matching**: Transform AI text to match your writing style
        - **Customization**: Adjust settings to control how much of your style is applied
        - **Analytics**: Get insights into your writing style characteristics
        - **Multiple Profiles**: Create different style profiles for different contexts
        
        #### How It Works:
        
        1. We analyze samples of your writing to identify your unique style patterns
        2. Our AI models learn these patterns and apply them to new content
        3. You get text that sounds like you wrote it, not an AI
        
        #### Privacy & Security:
        
        Your writing samples and transformed texts are kept private and secure. We do not use your content to train our models for other users.
        """)
    
    # Sidebar
    with st.sidebar:
        st.header("streamlit app")
        
        # Account section
        st.subheader("Account")
        
        if is_authenticated():
            if "user" in st.session_state:
                username = st.session_state.user.get('username', 'User')
                st.success(f"You are logged in as: {username}")
            else:
                st.success("You are logged in")
                
            if st.button("Logout"):
                from auth import logout_user
                logout_user()
                st.rerun()
        else:
            st.warning("You are not logged in.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Login"):
                    st.switch_page("pages/login_fixed.py")
            with col2:
                if st.button("Register"):
                    st.switch_page("pages/register.py")
        
        # Style Profiles
        st.subheader("Style Profiles")
        
        if is_authenticated():
            profile_options = ["None (Use Basic Style)", "Professional", "Casual", "Academic", "Creative"]
            selected_profile = st.selectbox("Select a style profile:", profile_options)
            
            if selected_profile != "None (Use Basic Style)":
                st.info(f"Using {selected_profile} style profile")
            
            with st.expander("Create New Profile"):
                st.text_input("Profile Name:")
                st.text_area("Sample Text (for style analysis):", height=100)
                st.button("Create Profile")
        else:
            st.info("Log in to create and use style profiles")
    
    # Footer
    st.markdown(
        """
        <div class="footer">
            <p>© 2025 Humanyze. All rights reserved.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
