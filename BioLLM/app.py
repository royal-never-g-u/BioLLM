import streamlit as st
import sys
import os
import re
import warnings
import traceback

# Show all warnings
warnings.filterwarnings("always")

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from BioLLM.main import main as biomain, strip_command

def extract_model_name_from_analyse(user_input):
    """
    Extract model name from analyse command
    
    Args:
        user_input (str): User input containing analyse command
        
    Returns:
        str: Model name if found, None otherwise
    """
    if not user_input:
        return None
    
    # Remove 'analyse' command and get the rest
    user_input_lower = user_input.lower().strip()
    if user_input_lower.startswith('analyse'):
        # Extract everything after 'analyse'
        model_part = user_input[7:].strip()  # 7 is length of 'analyse'
        if model_part:
            # Clean up the model name - remove extra spaces and quotes
            model_part = model_part.strip().strip('"').strip("'")
            return model_part
    return None

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
    
    # Handle None or empty text
    if text is None or not isinstance(text, str):
        return detected_models
    
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
    # Handle None or empty text
    if text is None or not isinstance(text, str):
        st.markdown("No content to display")
        return
    
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
                if 'last_command' in st.session_state and st.session_state.last_command is not None:
                    last_cmd = st.session_state.last_command.lower()
                    is_knowledge_response = (last_cmd == 'knowledge')
                
                if is_knowledge_response:
                    # Check for models in assistant responses
                    if message["content"] is not None:
                        detected_models = detect_models_in_text(message["content"], models)
                        display_text_with_model_buttons(message["content"], detected_models)
                    else:
                        st.markdown("No content available")
                else:
                    # Regular display without model buttons
                    if message["content"] is not None:
                        st.markdown(message["content"])
                    else:
                        st.markdown("No content available")
            else:
                if message["content"] is not None:
                    st.markdown(message["content"])
                else:
                    st.markdown("No content available")

    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.history.append({"role": "user", "content": user_input})

        matched = False
        result = ""
        current_command = ""  # Track the current command being executed
        
        # Always call task_pick_agent to analyze user input for task type
        from agent.task_pick_agent import analyze_user_input_for_task_type
        
        st.info("🔍 正在分析用户输入以识别任务类型...")
        
        # Call task_pick_agent to analyze user input
        task_pick_result = analyze_user_input_for_task_type(user_input)
        
        if task_pick_result['success']:
            if task_pick_result['matched_task_type']:
                task_type = task_pick_result['matched_task_type']
                from analysis_types import get_analysis_type_description
                task_description = get_analysis_type_description(task_type)
                
                st.success(f"✅ 识别到任务类型: {task_type} - {task_description}")
                st.info("📝 已自动设置bio_task中的task_type字段")
            else:
                st.info("ℹ️ 未识别到特定的分析类型，继续正常处理")
        else:
            st.warning("⚠️ 任务类型分析失败，继续正常处理")
            st.error(f"错误: {task_pick_result.get('error', 'Unknown error')}")
        
        st.info("🔄 继续处理用户输入...")
        
        # Check if this is a response to experiment prompt
        if 'show_experiment_prompt' in st.session_state and st.session_state.show_experiment_prompt:
            from agent.judge_agent import judge_user_response
            from bio_task import update_current_task, get_current_task
            from experiment_executor import execute_gene_deletion
            
            # Use judge agent to determine user's intention
            wants_experiment = judge_user_response(user_input)
            
            if wants_experiment:
                st.success("✅ Great! Let's start experimenting with the model.")
                
                # Get the analyzed model information
                if 'experiment_prompt_model' in st.session_state:
                    model_name = st.session_state.experiment_prompt_model
                    model_location = f"../downloads/{model_name}.mat"  # Default location
                    
                    # Update bio_task with model information (preserve task_type)
                    try:
                        update_current_task(
                            model_name=model_name,
                            model_local=model_location
                            # Note: We don't update task_type here to preserve user's analysis type
                            # Only TaskPickAgent should update task_type when matching analysis types
                        )
                        st.info(f"📝 Model '{model_name}' saved to bio_task for experiments.")
                        
                        # Execute gene deletion method
                        with st.spinner(f"🔬 Running gene deletion analysis for {model_name}..."):
                            analysis_result = execute_gene_deletion(model_name, model_location)
                        
                        if analysis_result['success']:
                            st.success("✅ Gene deletion analysis completed successfully!")
                            
                            # Display analysis summary
                            if 'summary' in analysis_result['results']:
                                summary = analysis_result['results']['summary']
                                st.markdown("### 📊 Analysis Summary")
                                st.json(summary)
                            
                            # Display visualizations
                            if 'visualizations' in analysis_result['results']:
                                visualizations = analysis_result['results']['visualizations']
                                if visualizations:
                                    st.markdown("### 📈 Analysis Visualizations")
                                    for viz in visualizations:
                                        try:
                                            if viz['type'] == 'image':
                                                st.image(viz['path'], caption=viz['name'])
                                            elif viz['type'] == 'html':
                                                with open(viz['path'], 'r', encoding='utf-8') as f:
                                                    html_content = f.read()
                                                st.components.v1.html(html_content, height=600)
                                            st.success(f"✅ Displayed: {viz['name']}")
                                        except Exception as viz_error:
                                            st.error(f"❌ Error displaying {viz['name']}: {viz_error}")
                            
                            # Display reports
                            if 'report_paths' in analysis_result['results']:
                                report_paths = analysis_result['results']['report_paths']
                                if report_paths:
                                    st.markdown("### 📋 Analysis Reports")
                                    for report_type, report_path in report_paths.items():
                                        if os.path.exists(report_path):
                                            st.markdown(f"**{report_type.replace('_', ' ').title()}**")
                                            try:
                                                with open(report_path, 'r', encoding='utf-8') as f:
                                                    report_content = f.read()
                                                st.text_area(f"Report Content ({report_type})", report_content, height=300)
                                            except Exception as report_error:
                                                st.error(f"❌ Error reading report {report_type}: {report_error}")
                                            
                                            # Add LLM analysis of the results
                                            st.markdown("---")
                                            st.markdown("### 🤖 LLM Analysis of Results")
                                            
                                            try:
                                                from agent.gene_deletion_analysis_agent import analyze_gene_deletion_results
                                                
                                                llm_response = analyze_gene_deletion_results(model_name)
                                                st.markdown(llm_response)
                                                
                                            except Exception as llm_error:
                                                st.error(f"❌ Error generating LLM analysis: {llm_error}")
                        else:
                            st.error(f"❌ Gene deletion analysis failed: {analysis_result.get('error', 'Unknown error')}")
                            if 'traceback' in analysis_result:
                                with st.expander("Error Details"):
                                    st.code(analysis_result['traceback'])
                    
                    except Exception as e:
                        st.error(f"❌ Error during gene deletion analysis: {e}")
                        st.error(f"Full error details: {traceback.format_exc()}")
                
                # Clear experiment prompt state
                st.session_state.show_experiment_prompt = False
                if 'experiment_prompt_model' in st.session_state:
                    del st.session_state.experiment_prompt_model
                
                matched = True
                result = "Experiment completed successfully!"
                
            else:
                st.info("📝 No problem! You can always start experiments later.")
                st.info("💡 Use 'analyse [model_name]' to analyze other models.")
                
                # Clear experiment prompt state
                st.session_state.show_experiment_prompt = False
                if 'experiment_prompt_model' in st.session_state:
                    del st.session_state.experiment_prompt_model
                
                matched = True
                result = "Experiment prompt dismissed."
        
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
                        
                        # Try to download corresponding .mat file
                        with st.spinner(f"Downloading {found_model}.mat..."):
                            download_result = download_tool.download_model_from_name(found_model)
                        
                        if download_result['success']:
                            result += f"\n✓ {download_result['message']}"
                            result += f"\nFile saved to: {download_result['file_path']}"
                        else:
                            result += f"\n✗ Download failed: {download_result['message']}"
                        
                        matched = True
                    else:
                        # No specific model name identified, continue with subsequent agent command detection
                        # Don't set matched = True, let program continue with traditional commands and chat
                        result = f"No matching model found in your input. Available models: {', '.join(available_models)}\n\nContinuing with other commands..."
                        # Don't set matched = True, let program continue execution
            
            # Handle other virtual commands here if needed
            else:
                result = f"Virtual command '{command_name}' detected but not implemented yet."
                matched = True
        
        # Try traditional commands if no virtual command matched
        if not matched:
            try:
                for cmd, func in commands.items():
                    if user_input is not None and user_input.lower().startswith(cmd):
                        current_command = cmd
                        with st.spinner(f"Running command: {cmd}..."):
                            try:
                                if cmd in ['update_data', 'force_update']:
                                    result = func()
                                else:
                                    prompt = strip_command(user_input, cmd)
                                    result = func(prompt)
                                    
                                    # Check if this is an analyse command and get figures
                                    if cmd == 'analyse':
                                        # Extract model name from the analyse command
                                        model_name = extract_model_name_from_analyse(user_input)
                                        if model_name:
                                            st.session_state.current_analyzed_model = model_name
                                            st.success(f"✅ Model '{model_name}' analyzed successfully and ready for experiments!")
                                        else:
                                            st.warning("⚠️ Model name not found in command. Use format: 'analyse [model_name]'")
                                        
                                        # Get figures if available
                                        if hasattr(func.__self__, 'current_figures'):
                                            figures = func.__self__.current_figures
                                            if figures is not None:
                                                st.session_state.current_figures = figures
                                            # Removed debug messages for cleaner output
                                        # Removed debug messages for cleaner output
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
                if result is not None:
                    detected_models = detect_models_in_text(result, models)
                    if detected_models:
                        st.write(f"🔍 Found {len(detected_models)} model(s) in response")
                    display_text_with_model_buttons(result, detected_models)
                else:
                    st.markdown("No response content available")
            else:
                # Regular display without model buttons
                if result is not None:
                    st.markdown(result)
                else:
                    st.markdown("No response content available")
                
                # Display visualizations if available (for analyse command)
                if current_command == 'analyse' and 'current_figures' in st.session_state:
                    figures = st.session_state.current_figures
                    if figures is not None and figures:
                        st.markdown("### 📊 Model Analysis Visualizations")
                        
                        # Display each figure
                        for i, figure_data in enumerate(figures):
                            if isinstance(figure_data, dict):
                                # Handle dictionary format from new_model_analyzer_agent
                                title = figure_data.get('name', f'Figure {i+1}')
                                file_path = figure_data.get('path', '')
                                file_type = figure_data.get('type', 'image')
                                
                                st.markdown(f"**{title}**")
                                try:
                                    if file_type == 'image':
                                        # Display image file
                                        try:
                                            # Method 1: Try using file path directly
                                            st.image(file_path, caption=title)
                                        except Exception as e1:
                                            try:
                                                # Method 2: Try reading file and passing bytes
                                                with open(file_path, 'rb') as f:
                                                    image_bytes = f.read()
                                                    st.image(image_bytes, caption=title)
                                            except Exception as e2:
                                                # Method 3: Try using PIL
                                                from PIL import Image
                                                image = Image.open(file_path)
                                                st.image(image, caption=title)
                                    elif file_type == 'html':
                                        # Display HTML file content
                                        with open(file_path, 'r', encoding='utf-8') as f:
                                            html_content = f.read()
                                        st.components.v1.html(html_content, height=600)
                                    st.write(f"✅ Displayed {file_type} {i+1}: {title}")
                                except Exception as e:
                                    st.error(f"❌ Error displaying {file_type} {i+1}: {e}")
                            elif isinstance(figure_data, tuple) and len(figure_data) == 2:
                                # Handle tuple format (title, fig) from old model_analyzer_agent
                                title, fig = figure_data
                                st.markdown(f"**{title}**")
                                try:
                                    st.pyplot(fig)
                                    st.write(f"✅ Displayed figure {i+1}: {title}")
                                except Exception as e:
                                    st.error(f"❌ Error displaying figure {i+1}: {e}")
                            else:
                                st.error(f"❌ Unknown figure format: {type(figure_data)}")
                        
                        # Clear the figures from session state
                        del st.session_state.current_figures
                        
                        # Set experiment prompt state after successful analyse command with model name
                        if 'current_analyzed_model' in st.session_state:
                            model_name = st.session_state.current_analyzed_model
                            if model_name:  # Only if we have a valid model name
                                st.session_state.show_experiment_prompt = True
                                st.session_state.experiment_prompt_model = model_name
                                
                                # Display experiment prompt immediately after analyse command
                                st.markdown("---")
                                st.markdown("### 🧪 Experiment Prompt")
                                st.markdown("**Do you want to use this model for experiments?**")
                                st.markdown("*You can now perform experiments with the analyzed model using various commands.*")
                                st.markdown("*Please respond with 'yes' or 'no' in the chat input below.*")
                    else:
                        # Analyse command executed but no figures - still set experiment prompt if model name exists
                        if 'current_analyzed_model' in st.session_state:
                            model_name = st.session_state.current_analyzed_model
                            if model_name:  # Only if we have a valid model name
                                st.session_state.show_experiment_prompt = True
                                st.session_state.experiment_prompt_model = model_name
                                
                                # Display experiment prompt immediately after analyse command
                                st.markdown("---")
                                st.markdown("### 🧪 Experiment Prompt")
                                st.markdown("**Do you want to use this model for experiments?**")
                                st.markdown("*You can now perform experiments with the analyzed model using various commands.*")
                                st.markdown("*Please respond with 'yes' or 'no' in the chat input below.*")
                elif current_command == 'analyse':
                    # Analyse command executed but no figures in session state - still set experiment prompt if model name exists
                    if 'current_analyzed_model' in st.session_state:
                        model_name = st.session_state.current_analyzed_model
                        if model_name:  # Only if we have a valid model name
                            st.session_state.show_experiment_prompt = True
                            st.session_state.experiment_prompt_model = model_name
                            
                            # Display experiment prompt immediately after analyse command
                            st.markdown("---")
                            st.markdown("### 🧪 Experiment Prompt")
                            st.markdown("**Do you want to use this model for experiments?**")
                            st.markdown("*You can now perform experiments with the analyzed model using various commands.*")
                            st.markdown("*Please respond with 'yes' or 'no' in the chat input below.*")

        st.session_state.history.append({"role": "assistant", "content": result})

if __name__ == "__main__":
    main() 