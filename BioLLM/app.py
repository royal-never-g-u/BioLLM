import streamlit as st
import sys
import os
import re
import warnings
import traceback

# 显示所有警告
warnings.filterwarnings("always")

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from BioLLM.main import main as biomain, strip_command

def load_biosimulation_models():
    """Load biosimulation model names from the database file."""
    models = []
    try:
        # Try multiple possible paths
        possible_paths = [
            'BiosimulationModels.txt',  # Current directory
            'BioLLM/BiosimulationModels.txt',  # From parent directory
            '../BiosimulationModels.txt',  # From parent directory
        ]
        
        file_found = False
        for path in possible_paths:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            models.append(line)
                    file_found = True
                    break
            except FileNotFoundError:
                continue
        
        if not file_found:
            st.warning("BiosimulationModels.txt not found in any expected location")
            
    except Exception as e:
        st.warning(f"Error loading BiosimulationModels.txt: {e}")
    return models

def detect_models_in_text(text, models):
    """Detect model names in text and return positions for button creation."""
    detected_models = []
    text_lower = text.lower()
    
    # Create a mapping of common variations and aliases
    model_aliases = {
        'core e. coli metabolic model': 'e_coli_core',
        'e. coli core': 'e_coli_core',
        'e coli core': 'e_coli_core',
        'human erythrocyte metabolic network': 'Recon1',  # Assuming this refers to Recon1
        'human metabolic model': 'Recon1',  # Generic reference
        's. cerevisiae metabolic model': 'iMM904',  # Generic reference
        'yeast metabolic model': 'iMM904',  # Generic reference
    }
    
    # First, check for exact matches
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
    
    # Then check for aliases and variations
    for alias, canonical_model in model_aliases.items():
        if canonical_model in models:  # Only if the canonical model is in our list
            pattern = re.compile(re.escape(alias), re.IGNORECASE)
            matches = pattern.finditer(text)
            
            for match in matches:
                detected_models.append({
                    'model': canonical_model,
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
        
        # Deduplicate models to avoid multiple buttons for the same model
        unique_models = []
        seen_models = set()
        for detection in detected_models:
            if detection['model'] not in seen_models:
                unique_models.append(detection)
                seen_models.add(detection['model'])
        
        # Create buttons in a horizontal layout
        cols = st.columns(min(len(unique_models), 3))  # Max 3 columns
        
        for i, detection in enumerate(unique_models):
            col_idx = i % len(cols)
            with cols[col_idx]:
                # Create unique key using timestamp and position
                import time
                unique_key = f"model_btn_{detection['model']}_{int(time.time() * 1000)}_{i}_{hash(text)}"
                
                # Create button without any click functionality
                st.button(f"📊 {detection['model']}", 
                         key=unique_key,
                         help=f"Model: {detection['model']} (Click functionality disabled)",
                         use_container_width=True)
                # Note: Button click does nothing - functionality removed as requested



def main():
    st.title("BioLLM AI Agent")

    # Load biosimulation models
    try:
        models = load_biosimulation_models()
        st.info(f"Loaded {len(models)} biosimulation models")
    except Exception as e:
        st.error(f"ERROR loading biosimulation models: {e}")
        models = []

    # This will initialize all the agents and tools
    try:
        memory, commands = biomain(initialize_only=True)
        code_writer = commands["generate"].__self__ # A bit of a hack to get the agent
        st.info("Successfully initialized agents and tools")
    except Exception as e:
        st.error(f"ERROR initializing agents and tools: {e}")
        st.error(f"Full error details: {traceback.format_exc()}")
        return
    
    # Get the virtual command agent
    try:
        from BioLLM.agent.virtual_command_agent import VirtualCommandAgent
        virtual_command_agent = VirtualCommandAgent()
        st.info("Successfully initialized virtual command agent")
    except Exception as e:
        st.error(f"ERROR initializing virtual command agent: {e}")
        st.error(f"Full error details: {traceback.format_exc()}")
        return

    if 'history' not in st.session_state:
        st.session_state.history = []

    # Get user input
    user_input = st.chat_input("Ask BioLLM anything...")

    # Display chat history with model buttons (only for knowledge responses)
    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # Only show model buttons for knowledge command responses
                # Check if this response was from the knowledge command
                is_knowledge_response = False
                if 'last_command' in st.session_state:
                    last_cmd = st.session_state.last_command.lower()
                    is_knowledge_response = (last_cmd == 'knowledge')
                
                if is_knowledge_response:
                    # Check for models in assistant responses
                    detected_models = detect_models_in_text(message["content"], models)
                    display_text_with_model_buttons(message["content"], detected_models)
                else:
                    # Regular display without model buttons
                    st.markdown(message["content"])
            else:
                st.markdown(message["content"])

    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.history.append({"role": "user", "content": user_input})

        matched = False
        result = ""
        current_command = ""  # Track the current command being executed
        
        # Check for virtual command matches
        virtual_match = virtual_command_agent.match_command(user_input)
        
        # Handle virtual commands
        if virtual_match['matched'] and virtual_match['confidence'] >= 0.1:
            command_name = virtual_match['command_name']
            current_command = command_name
            
            # Handle choose_model virtual command
            if command_name == 'choose_model':
                # Get available biosimulation models
                from BioLLM.agent.rag_tool import RAGTool
                from BioLLM.agent.download_tool import DownloadTool
                from BioLLM.main import extract_model_name
                
                rag_tool = RAGTool()
                download_tool = DownloadTool()
                
                available_models = rag_tool.get_saved_biosimulation_models()
                
                if not available_models:
                    result = "No biosimulation models found in the database. Please run 'update_data' or 'force_update' first to extract models from scientific papers."
                    matched = True
                else:
                    # Extract model name from user input
                    found_model = extract_model_name(user_input, available_models)
                    
                    if found_model:
                        result = f"Selected biosimulation model: {found_model}"
                        
                        # 尝试下载对应的.mat文件
                        with st.spinner(f"Downloading {found_model}.mat..."):
                            download_result = download_tool.download_model_from_name(found_model)
                        
                        if download_result['success']:
                            result += f"\n✓ {download_result['message']}"
                            result += f"\nFile saved to: {download_result['file_path']}"
                        else:
                            result += f"\n✗ Download failed: {download_result['message']}"
                        
                        matched = True
                    else:
                        # 没有识别到具体model name，继续执行后面的agent命令判别
                        # 不设置matched = True，让程序继续执行传统命令和chat
                        result = f"No matching model found in your input. Available models: {', '.join(available_models)}\n\nContinuing with other commands..."
                        # 不设置matched = True，让程序继续执行
            
            # Handle other virtual commands here if needed
            else:
                result = f"Virtual command '{command_name}' detected but not implemented yet."
                matched = True
        
        # Try traditional commands if no virtual command matched
        if not matched:
            try:
                for cmd, func in commands.items():
                    if user_input.lower().startswith(cmd):
                        current_command = cmd
                        with st.spinner(f"Running command: {cmd}..."):
                            try:
                                if cmd in ['update_data', 'force_update']:
                                    result = func()
                                else:
                                    prompt = strip_command(user_input, cmd)
                                    result = func(prompt)
                                    
                                    # Check if this is an analyse command and get figures
                                    if cmd == 'analyse' and hasattr(func.__self__, 'current_figures'):
                                        figures = func.__self__.current_figures
                                        if figures is not None:
                                            st.session_state.current_figures = figures
                                            st.write(f"Debug: Stored {len(figures)} figures in session state")
                                        else:
                                            st.write("Debug: analyse command executed but current_figures is None")
                                    elif cmd == 'analyse':
                                        st.write("Debug: analyse command executed but no current_figures attribute found")
                            except Exception as e:
                                st.error(f"ERROR executing command '{cmd}': {e}")
                                st.error(f"Full error details: {traceback.format_exc()}")
                                result = f"Error executing command '{cmd}': {e}"
                        matched = True
                        break
            except Exception as e:
                st.error(f"ERROR in command matching: {e}")
                st.error(f"Full error details: {traceback.format_exc()}")
        
        if not matched:
            try:
                with st.spinner("Generating response..."):
                    result = code_writer.chat(user_input, memory)
            except Exception as e:
                st.error(f"ERROR generating response: {e}")
                st.error(f"Full error details: {traceback.format_exc()}")
                result = f"Error generating response: {e}"

        # Store the current command for determining if model buttons should be shown
        st.session_state.last_command = current_command

        # Check for models in the result and create buttons (only for knowledge command)
        is_knowledge_command = (current_command == 'knowledge')
        
        with st.chat_message("assistant"):
            if is_knowledge_command:
                # Show model buttons for knowledge command responses
                detected_models = detect_models_in_text(result, models)
                if detected_models:
                    st.write(f"🔍 Found {len(detected_models)} model(s) in response")
                display_text_with_model_buttons(result, detected_models)
            else:
                # Regular display without model buttons
                st.markdown(result)
                
                # Display visualizations if available (for analyse command)
                if current_command == 'analyse' and 'current_figures' in st.session_state:
                    figures = st.session_state.current_figures
                    if figures is not None:
                        st.write(f"Debug: Found {len(figures)} figures in session state")
                        if figures:
                            st.markdown("### 📊 Model Analysis Visualizations")
                            
                            # Display each figure
                            for i, (title, fig) in enumerate(figures):
                                st.markdown(f"**{title}**")
                                try:
                                    st.pyplot(fig)
                                    st.write(f"✅ Displayed figure {i+1}: {title}")
                                except Exception as e:
                                    st.error(f"❌ Error displaying figure {i+1}: {e}")
                            
                            # Clear the figures from session state
                            del st.session_state.current_figures
                        else:
                            st.write("Debug: No figures found in session state")
                    else:
                        st.write("Debug: No figures found in session state")
                elif current_command == 'analyse':
                    st.write("Debug: analyse command executed but no figures in session state")
        
        st.session_state.history.append({"role": "assistant", "content": result})

if __name__ == "__main__":
    main() 