#!/usr/bin/env python3
"""
Simple demo to show model button functionality in Streamlit
"""

import streamlit as st
import sys
import os
import re

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def load_biosimulation_models():
    """Load biosimulation model names from the database file."""
    models = []
    try:
        with open('BioLLM/BiosimulationModels.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    models.append(line)
    except FileNotFoundError:
        st.warning("BiosimulationModels.txt not found")
    return models

def detect_models_in_text(text, models):
    """Detect model names in text and return positions for button creation."""
    detected_models = []
    text_lower = text.lower()
    
    for model in models:
        # Find all occurrences of the model name (case-insensitive)
        pattern = re.compile(re.escape(model), re.IGNORECASE)
        matches = pattern.finditer(text)
        
        for match in matches:
            detected_models.append({
                'model': model,
                'start': match.start(),
                'end': match.end(),
                'original_text': text[match.start():match.end()]
            })
    
    # Sort by position to avoid overlapping
    detected_models.sort(key=lambda x: x['start'])
    return detected_models

def display_text_with_model_buttons(text, detected_models):
    """Display text with clickable buttons for detected models using Streamlit components."""
    # First display the text normally
    st.markdown(text)
    
    # Then display buttons for detected models if any
    if detected_models:
        st.markdown("**Available models in this response:**")
        
        # Create buttons in a horizontal layout
        cols = st.columns(min(len(detected_models), 3))  # Max 3 columns
        
        for i, detection in enumerate(detected_models):
            col_idx = i % len(cols)
            with cols[col_idx]:
                # Create unique key using timestamp and position
                import time
                unique_key = f"model_btn_{detection['model']}_{int(time.time() * 1000)}_{i}_{hash(text)}"
                
                if st.button(f"📊 {detection['model']}", 
                            key=unique_key,
                            help=f"Click to use {detection['model']} for experiment",
                            use_container_width=True):
                    # Simulate user input for model selection
                    st.session_state.model_selection = f"I want to use {detection['model']} for the experiment"
                    st.rerun()

def main():
    st.title("Model Button Feature Demo")
    
    # Load models
    models = load_biosimulation_models()
    
    st.write("This demo shows how the model detection and button feature works.")
    st.write(f"Loaded {len(models)} models from BiosimulationModels.txt")
    
    # Demo responses with models
    demo_responses = [
        "The iMM904 model is excellent for metabolic analysis. You can also consider using Recon1 for human metabolism studies.",
        "For E. coli studies, I recommend using the e_coli_core model. The iND750 model is also available for more complex analyses.",
        "This response has no model names mentioned.",
        "The core E. coli metabolic model and human erythrocyte metabolic network are both useful for different types of studies."
    ]
    
    st.subheader("Demo Responses with Model Detection")
    
    for i, response in enumerate(demo_responses):
        st.write(f"**Response {i+1}:**")
        detected_models = detect_models_in_text(response, models)
        display_text_with_model_buttons(response, detected_models)
        st.divider()
    
    # Show what happens when a button is clicked
    if 'model_selection' in st.session_state:
        st.success(f"Button clicked! Would trigger: {st.session_state.model_selection}")
        
        # Show the virtual command matching
        from BioLLM.agent.virtual_command_agent import VirtualCommandAgent
        agent = VirtualCommandAgent()
        result = agent.match_command(st.session_state.model_selection)
        
        st.info(f"Virtual command match result:")
        st.info(f"  Matched: {result['matched']}")
        st.info(f"  Command: {result['command_name']}")
        st.info(f"  Confidence: {result['confidence']:.2f}")
        
        if result['matched'] and result['command_name'] == 'choose_model':
            st.success("✅ This would trigger the choose_model virtual command!")
            st.success("✅ The system would then download the corresponding .mat file")
        else:
            st.error("❌ This would not trigger the choose_model command")
        
        del st.session_state.model_selection

if __name__ == "__main__":
    main() 