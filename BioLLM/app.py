import streamlit as st
import sys
import os
import re
import warnings
import traceback
import json

# Suppress asyncio-related warnings but show others
warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed event loop.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="asyncio")
warnings.filterwarnings("default")  # Show other warnings

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from BioLLM.main import main as biomain, strip_command
from experiment_state_machine import (
    get_state_machine, 
    handle_analyse_agent_response, 
    handle_explain_agent_response,
    get_current_state_info,
    reset_state_machine
)
from result_visualizer import get_result_visualizer
from enhanced_llm_analyzer import get_enhanced_llm_analyzer

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

    # Initialize session state variables only once
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    
    if not st.session_state.initialized:
        # Load biosimulation models
        try:
            models = load_biosimulation_models()
            st.info(f"Loaded {len(models)} biosimulation models")
        except Exception as e:
            st.error(f"ERROR loading biosimulation models: {e}")
            models = []

        # This will initialize all the agents and tools
        try:
            memory, commands = biomain(initialize_only=True, initialize_bio_task_flag=True)
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
        
        # Get the agent-for-agent
        try:
            from BioLLM.agent.agent_for_agent import AgentForAgent
            agent_for_agent = AgentForAgent()
            st.info("Successfully initialized agent-for-agent")
        except Exception as e:
            st.error(f"ERROR initializing agent-for-agent: {e}")
            st.error(f"Full error details: {traceback.format_exc()}")
            return

        # Store models and agents in session state for reuse
        st.session_state.models = models
        st.session_state.memory = memory
        st.session_state.commands = commands
        st.session_state.code_writer = code_writer
        st.session_state.virtual_command_agent = virtual_command_agent
        st.session_state.agent_for_agent = agent_for_agent
        st.session_state.initialized = True
        
        st.success("🚀 BioLLM initialized successfully!")
    else:
        # Use stored values from session state
        models = st.session_state.models
        memory = st.session_state.memory
        commands = st.session_state.commands
        code_writer = st.session_state.code_writer
        virtual_command_agent = st.session_state.virtual_command_agent
        agent_for_agent = st.session_state.agent_for_agent

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
        
        st.info("🔍 Analyzing user input to identify task type...")
        
        # Call task_pick_agent to analyze user input
        task_pick_result = analyze_user_input_for_task_type(user_input)
        
        if task_pick_result['success']:
            if task_pick_result['matched_task_type']:
                task_type = task_pick_result['matched_task_type']
                from analysis_types import get_analysis_type_description
                task_description = get_analysis_type_description(task_type)
                
                st.success(f"✅ Identified task type: {task_type} - {task_description}")
                st.info("📝 Automatically set task_type field in bio_task")
                
                # Check if if_next_step was triggered by task_pick_agent
                if task_pick_result.get('next_step_triggered', False):
                    st.success("🎯 Complete configuration detected, automatically analyzing next steps...")
                    
                    next_step_result = task_pick_result.get('next_step_result')
                    if next_step_result and next_step_result.get('success'):
                        st.success("✅ Next step analysis completed!")
                        
                        # Display additional information based on action type
                        print(f"🔍 DEBUG: Processing next_step_result action: {next_step_result['action']}")
                        if next_step_result['action'] == 'both_available':
                            # Call explanation agent to provide detailed explanation
                            print(f"🔍 DEBUG: Calling explanation_agent for both_available case")
                            from agent.explanation_agent import generate_model_explanation
                            
                            model_name = next_step_result.get('model_name')
                            task_type = next_step_result.get('task_type')
                            
                            print(f"🔍 DEBUG: model_name: {model_name}, task_type: {task_type}")
                            
                            with st.spinner(f"🔍 Generating explanation for {model_name} with task type {task_type}..."):
                                explanation_result = generate_model_explanation(model_name, task_type)
                            
                            if explanation_result:
                                # Store explanation result for display in chat message
                                st.session_state.explanation_result = explanation_result
                                
                                # Set explanation prompt state for user response handling
                                st.session_state.show_explanation_prompt = True
                                st.session_state.explanation_prompt_model = model_name
                                st.session_state.explanation_prompt_task_type = task_type
                                
                                # Set flag to indicate that explanation_agent has been called
                                st.session_state.explanation_agent_called = True
                            else:
                                # Store error message for display in chat message
                                st.session_state.next_step_explanation_error_message = "❌ Failed to generate explanation"
                            
                        elif next_step_result['action'] == 'model_only':
                            # Store info message for display in chat message
                            st.session_state.next_step_model_only_message = "📋 Please select a task type to proceed with the analysis."
                        elif next_step_result['action'] == 'task_only':
                            # Store info message for display in chat message
                            st.session_state.next_step_task_only_message = "🔍 Model recommendation provided. Please select a model to proceed."
                        else:
                            # Store info message for display in chat message
                            st.session_state.next_step_complete_config_message = "ℹ️ Please complete your configuration to proceed."
                    else:
                        # Store error message for display in chat message
                        st.session_state.next_step_analysis_error_message = f"❌ Next step analysis failed: {next_step_result.get('error', 'Unknown error') if next_step_result else 'No result'}"
                
            else:
                # Store info message for display in chat message
                st.session_state.no_analysis_type_message = "ℹ️ No specific analysis type identified, continuing with normal processing"
        else:
            # Store warning and error messages for display in chat message
            st.session_state.task_pick_warning_message = "⚠️ Task type analysis failed, continuing with normal processing"
            st.session_state.task_pick_error_message = f"Error: {task_pick_result.get('error', 'Unknown error')}"
        
        # Store info message for display in chat message
        st.session_state.continue_processing_message = "🔄 Continuing to process user input..."
        

        
        # Check for virtual command matches first (before explanation prompt)
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
                            result += f"\nThe model was not found. Please try other models."
                        
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
        
        # Check if this is a response to analyse agent prompt (after virtual commands)
        # Only trigger if user input looks like a yes/no response
        elif ('show_analyse_prompt' in st.session_state and 
              st.session_state.show_analyse_prompt and 
              user_input.lower().strip() in ['yes', 'no', 'y', 'n', 'agree', 'disagree', 'ok', 'not ok']):
            
            # Get the analyse prompt information
            if 'analyse_prompt_model' in st.session_state and 'analyse_prompt_task_type' in st.session_state:
                model_name = st.session_state.analyse_prompt_model
                task_type = st.session_state.analyse_prompt_task_type
                
                # Handle analyse agent response using state machine
                transition_result = handle_analyse_agent_response(user_input, model_name, task_type)
                
                if transition_result['transition_successful']:
                    # Store success message for display in chat message
                    st.session_state.transition_success_message = transition_result['message']
                    
                    # Update bio_task with model information when user confirms
                    try:
                        from bio_task import update_current_task
                        model_location = f"../downloads/{model_name}.mat"
                        update_success = update_current_task(
                            model_name=model_name,
                            model_local=model_location
                        )
                        if update_success:
                            print(f"✅ Updated bio_task with model: {model_name}, location: {model_location}")
                        else:
                            print(f"❌ Failed to update bio_task with model: {model_name}")
                    except Exception as e:
                        print(f"❌ Error updating bio_task: {e}")
                    
                    # Check if we should proceed to explanation agent or if_next_step
                    try:
                        from bio_task import get_current_task
                        current_task = get_current_task()
                        has_model_name = bool(current_task.model_name and current_task.model_name.strip())
                        has_task_type = current_task.task_type is not None and current_task.task_type != ""
                        
                        print(f"🔍 DEBUG: bio_task check - model_name: '{current_task.model_name}', task_type: '{current_task.task_type}'")
                        print(f"🔍 DEBUG: has_model_name: {has_model_name}, has_task_type: {has_task_type}")
                        print(f"🔍 DEBUG: transition_result['new_state'].value: {transition_result['new_state'].value}")
                        
                        if has_model_name and has_task_type and transition_result['new_state'].value == 2:  # ANALYSIS_CONFIRMED
                            # Both model_name and task_type exist, call explanation agent
                            from agent.explanation_agent import generate_model_explanation
                            
                            with st.spinner(f"🔍 Generating explanation for {model_name} with task type {task_type}..."):
                                explanation_result = generate_model_explanation(model_name, task_type)
                        elif has_model_name and not has_task_type and transition_result['new_state'].value == 2:  # ANALYSIS_CONFIRMED
                            # Only model_name exists, call if_next_step to provide experiment options
                            print(f"🔍 DEBUG: Calling if_next_step for model_only case")
                            from agent.next_step_agent import if_next_step
                            
                            with st.spinner(f"🔍 Analyzing available experiments for {model_name}..."):
                                next_step_result = if_next_step()
                            
                            print(f"🔍 DEBUG: if_next_step result: {next_step_result}")
                            
                            if next_step_result and next_step_result.get('success'):
                                # Store next step result for display
                                st.session_state.next_step_result = next_step_result
                                explanation_result = None
                                print(f"✅ if_next_step executed successfully: {next_step_result.get('action', 'unknown')}")
                            else:
                                explanation_result = None
                                print(f"❌ if_next_step failed: {next_step_result.get('error', 'Unknown error') if next_step_result else 'No result'}")
                        else:
                            # Don't call explanation agent if bio_task is not complete
                            explanation_result = None
                            print(f"ℹ️ Skipping explanation agent: model_name={'有' if has_model_name else '无'}, task_type={'有' if has_task_type else '无'}")
                    except Exception as e:
                        print(f"❌ Error checking bio_task completeness: {e}")
                        explanation_result = None
                    
                    # Handle explanation_result or next_step_result
                    if explanation_result:
                        # Store explanation result for display in chat message
                        st.session_state.explanation_result = explanation_result
                        
                        # Set explanation prompt state for user response handling
                        st.session_state.show_explanation_prompt = True
                        st.session_state.explanation_prompt_model = model_name
                        st.session_state.explanation_prompt_task_type = task_type
                        
                        # Store explanation prompt information in session state for later display
                        st.session_state.pending_prompt = {
                            'type': 'explanation_agent',
                            'title': '📋 Explanation Agent Prompt',
                            'message': f"**Do you want to proceed with the experiment for model '{model_name}'?**",
                            'instruction': "*Please respond with 'yes' or 'no' in the chat input below.*"
                        }
                    else:
                        # Check if we have next_step_result from if_next_step
                        if 'next_step_result' in st.session_state and st.session_state.next_step_result:
                            # Don't set explanation prompt, next_step_result will be handled in result message
                            pass
                        elif has_model_name and has_task_type:
                            # Store error message for display in chat message
                            st.session_state.explanation_error_message = "❌ Failed to generate explanation"
                            # Reset state machine on failure
                            reset_state_machine()
                        else:
                            # Store info message for display in chat message
                            st.session_state.incomplete_config_message = "📋 Configuration incomplete. Please specify a task type to proceed."
                            # Reset state machine
                            reset_state_machine()
                else:
                    # Store error message for display in chat message
                    st.session_state.transition_error_message = f"❌ State transition failed: {transition_result['message']}"
                
                # Clear analyse prompt state
                st.session_state.show_analyse_prompt = False
                if 'analyse_prompt_model' in st.session_state:
                    del st.session_state.analyse_prompt_model
                if 'analyse_prompt_task_type' in st.session_state:
                    del st.session_state.analyse_prompt_task_type
                # Note: Don't clear pending_prompt and explanation_result here
                # They will be cleared after display in the chat message
                
                matched = True
                # Create a comprehensive result message for analysis prompt handling
                result = f"✅ Analysis prompt handled successfully!\n\n"
                result += f"**Model**: {model_name}\n"
                result += f"**Task Type**: {task_type}\n"
                result += f"**Status**: Analysis confirmed\n\n"
                
                print(f"🔍 DEBUG: Creating result message for analysis prompt")
                print(f"🔍 DEBUG: model_name: {model_name}, task_type: {task_type}")
                
                if transition_result['transition_successful']:
                    if transition_result['new_state'].value == 2:  # ANALYSIS_CONFIRMED
                        # Check if bio_task is complete
                        try:
                            from bio_task import get_current_task
                            current_task = get_current_task()
                            has_model_name = bool(current_task.model_name and current_task.model_name.strip())
                            has_task_type = current_task.task_type is not None and current_task.task_type != ""
                            
                            if has_model_name and has_task_type:
                                result += "🔄 **Next Step**: Explanation agent will provide detailed information.\n\n"
                                
                                # Add explanation result if available
                                if 'explanation_result' in st.session_state and st.session_state.explanation_result:
                                    result += "---\n\n"
                                    result += "### 📋 Model and Task Explanation\n\n"
                                    result += st.session_state.explanation_result + "\n\n"
                                
                                # Add pending prompt if available
                                if 'pending_prompt' in st.session_state and st.session_state.pending_prompt:
                                    prompt_info = st.session_state.pending_prompt
                                    result += "---\n\n"
                                    result += f"### {prompt_info['title']}\n\n"
                                    result += prompt_info['message'] + "\n\n"
                                    result += prompt_info['instruction'] + "\n\n"
                            elif has_model_name and not has_task_type:
                                # Only model_name exists, show next_step_result
                                print(f"🔍 DEBUG: Processing model_only case in result message generation")
                                if 'next_step_result' in st.session_state and st.session_state.next_step_result:
                                    next_step_result = st.session_state.next_step_result
                                    print(f"🔍 DEBUG: Found next_step_result: {next_step_result.get('action', 'unknown')}")
                                    # Only show the LLM-generated message, not the raw experiment list
                                    result += next_step_result.get('message', 'No message available') + "\n\n"
                                else:
                                    print(f"🔍 DEBUG: No next_step_result found in session state")
                                    result += "📋 **Status**: Configuration incomplete. Please specify a task type to proceed.\n\n"
                            else:
                                result += "📋 **Status**: Configuration incomplete. Please specify a task type to proceed.\n\n"
                        except Exception as e:
                            result += f"❌ **Error**: Failed to check configuration: {e}\n\n"
                    else:
                        result += "📝 **Status**: Analysis cancelled.\n\n"
                else:
                    result += f"❌ **Error**: {transition_result['message']}\n\n"
                
                # Clear next_step_result after result message generation
                if 'next_step_result' in st.session_state:
                    del st.session_state.next_step_result
            else:
                st.error("❌ Missing analyse prompt parameters")
                matched = True
        
        # Check if this is a response to explanation prompt (after virtual commands)
        # Only trigger if user input looks like a yes/no response
        elif ('show_explanation_prompt' in st.session_state and 
              st.session_state.show_explanation_prompt and 
              user_input.lower().strip() in ['yes', 'no', 'y', 'n', 'agree', 'disagree', 'ok', 'not ok']):
            
            # Get the explanation prompt information
            if 'explanation_prompt_model' in st.session_state and 'explanation_prompt_task_type' in st.session_state:
                model_name = st.session_state.explanation_prompt_model
                task_type = st.session_state.explanation_prompt_task_type
                
                # Get the latest task_type from bio_task to ensure consistency
                try:
                    from bio_task import get_current_task
                    current_task = get_current_task()
                    if current_task.task_type is not None and current_task.task_type != "":
                        task_type = current_task.task_type
                        print(f"🔍 DEBUG: Using latest task_type from bio_task: {task_type}")
                except Exception as e:
                    print(f"🔍 DEBUG: Failed to get latest task_type from bio_task: {e}")
                
                # Handle explain agent response using state machine
                transition_result = handle_explain_agent_response(user_input, model_name, task_type)
                
                if transition_result['transition_successful']:
                    # Store success message for display in chat message
                    st.session_state.experiment_transition_success_message = transition_result['message']
                    
                    # Check if experiment should be executed
                    if transition_result['should_execute_experiment']:
                        experiment_params = transition_result['experiment_params']
                        
                        # Execute experiment
                        with st.spinner(f"🔬 Executing experiment for {experiment_params['model_name']} with task type {experiment_params['task_type']}..."):
                            from experiment_executor import execute_experiment
                            experiment_result = execute_experiment(experiment_params['model_name'], experiment_params['task_type'])
                        
                        if experiment_result['success']:
                            # Store success message for display in chat message
                            st.session_state.experiment_success_message = "✅ Experiment executed successfully!"
                            
                            # Store experiment result for later display in chat message
                            st.session_state.last_experiment_result = experiment_result
                            st.session_state.experiment_task_type = experiment_result.get('task_type') or experiment_result.get('experiment_task_type')
                            
                            # Use enhanced result visualizer
                            result_visualizer = get_result_visualizer()
                            
                            # Check if this is a gene deletion experiment
                            task_type = experiment_result.get('task_type') or experiment_result.get('experiment_task_type')
                            if task_type == 1:  # FBA Analysis
                                # Store visualization data for later display
                                st.session_state.show_fba_visualization = True
                                st.session_state.fba_analysis_result = experiment_result
                            elif task_type == 2:  # Gene deletion analysis
                                # Store visualization data for later display
                                st.session_state.show_gene_deletion_visualization = True
                                
                                # Generate enhanced LLM analysis
                                enhanced_analyzer = get_enhanced_llm_analyzer()
                                llm_analysis = enhanced_analyzer.analyze_gene_deletion_results(experiment_result)
                                st.session_state.gene_deletion_llm_analysis = llm_analysis
                            elif task_type == 6:  # Constraint-Based Analysis
                                # Store visualization data for later display
                                st.session_state.show_constraint_based_visualization = True
                                st.session_state.constraint_based_analysis_result = experiment_result
                            else:
                                # Store experiment result for display in chat message
                                st.session_state.experiment_result = experiment_result
                            
                        else:
                            # Store error message for display in chat message
                            st.session_state.experiment_error_message = f"❌ Experiment execution failed: {experiment_result.get('error', 'Unknown error')}"
                            if 'traceback' in experiment_result:
                                st.session_state.experiment_error_traceback = experiment_result['traceback']
                    else:
                        # Store info message for display in chat message
                        st.session_state.experiment_cancelled_message = "📝 No problem! You can always execute experiments later."
                else:
                    # Store error message for display in chat message
                    st.session_state.experiment_transition_error_message = f"❌ State transition failed: {transition_result['message']}"
                
                # Clear explanation prompt state
                st.session_state.show_explanation_prompt = False
                if 'explanation_prompt_model' in st.session_state:
                    del st.session_state.explanation_prompt_model
                if 'explanation_prompt_task_type' in st.session_state:
                    del st.session_state.explanation_prompt_task_type
                # Note: pending_prompt and explanation_result will be cleared after display to prevent overwriting
                
                matched = True
                # Store the experiment result for display instead of a simple message
                if 'experiment_result' in locals():
                    # Create a comprehensive result message
                    result = f"✅ Experiment completed successfully!\n\n"
                    result += f"**Model**: {experiment_params['model_name']}\n"
                    result += f"**Task Type**: {experiment_params['task_type']}\n"
                    result += f"**Status**: Success\n\n"
                    
                    # Add experiment details if available
                    if 'experiment_result' in locals() and experiment_result:
                        if 'message' in experiment_result:
                            result += f"**Details**: {experiment_result['message']}\n\n"
                        if 'timestamp' in experiment_result:
                            result += f"**Timestamp**: {experiment_result['timestamp']}\n\n"
                    
                    # Store the full experiment result in session state for later use
                    st.session_state.last_experiment_result = experiment_result
                else:
                    result = "✅ Experiment completed successfully!"
            else:
                st.error("❌ Missing explanation prompt parameters")
                matched = True
            

        
        # Agent for Agent - Check if input is related to biological research (if no command matched yet)
        if not matched:
            # First check if user input already contains a regular command
            cmd_lower = user_input.lower().strip()
            contains_regular_command = False
            for cmd in commands.keys():
                if cmd_lower.startswith(cmd):
                    contains_regular_command = True
                    break
            
            # If no regular command found, check biological relevance
            if not contains_regular_command:
                with st.spinner("🤖 Agent for Agent: Checking biological relevance..."):
                    agent_result = agent_for_agent.check_biological_relevance(user_input)
                
                if agent_result['is_relevant']:
                    st.info(f"🧬 Biological relevance detected (confidence: {agent_result['confidence']:.2f})")
                    st.info(f"💭 Reasoning: {agent_result['reasoning']}")
                    st.info(f"🔄 Converting to knowledge command...")
                    
                    # Use the modified input for further processing
                    user_input = agent_result['modified_input']
                    st.success(f"✅ Input automatically enhanced: '{user_input}'")
                else:
                    st.info(f"ℹ️ Agent for Agent: Not biologically relevant (confidence: {agent_result['confidence']:.2f})")
        
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
                                            
                                            # Set up analyse agent prompt for state machine
                                            # Get task type from bio_task or use default
                                            try:
                                                from bio_task import get_current_task
                                                current_task = get_current_task()
                                                task_type = current_task.task_type
                                            except:
                                                task_type = 2  # Default to gene deletion analysis
                                            
                                            # Set analyse agent prompt state
                                            st.session_state.show_analyse_prompt = True
                                            st.session_state.analyse_prompt_model = model_name
                                            st.session_state.analyse_prompt_task_type = task_type
                                            
                                            # Store prompt information in session state for later display
                                            st.session_state.pending_prompt = {
                                                'type': 'analyse_agent',
                                                'title': '🔬 Analyse Agent Prompt',
                                                'message': f"**Do you want to use this model '{model_name}' for experiment?**",
                                                'instruction': "*Please respond with 'yes' or 'no' in the chat input below.*"
                                            }
                                            
                                            # Add the analyse success message and prompt to the result
                                            result += f"\n\n✅ Model '{model_name}' analyzed successfully and ready for experiments!\n\n"
                                            
                                            # Add pending prompt to result if available
                                            if 'pending_prompt' in st.session_state and st.session_state.pending_prompt:
                                                prompt_info = st.session_state.pending_prompt
                                                result += "---\n\n"
                                                result += f"### {prompt_info['title']}\n\n"
                                                result += prompt_info['message'] + "\n\n"
                                                result += prompt_info['instruction'] + "\n\n"
                                        else:
                                            # Store warning message for display in chat message
                                            st.session_state.analyse_warning_message = "⚠️ Model name not found in command. Use format: 'analyse [model_name]'"
                                            # Clear any previous figures when analysis fails
                                            if 'current_figures' in st.session_state:
                                                del st.session_state.current_figures
                                        
                                        # Get figures if available (only for successful analysis)
                                        if model_name and hasattr(func.__self__, 'current_figures'):
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
            # Check if explanation_agent has been called by task_pick_agent
            if 'explanation_agent_called' in st.session_state and st.session_state.explanation_agent_called:
                # Explanation agent has been called, don't generate default LLM response
                result = ""
                # Clear the flag
                del st.session_state.explanation_agent_called
            else:
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
            # Check if explanation_agent has been called and display its result
            if 'explanation_result' in st.session_state and st.session_state.explanation_result:
                st.markdown(st.session_state.explanation_result)
                # Clear the explanation result after display
                del st.session_state.explanation_result
            # Check if experiment result is available and display it
            elif 'experiment_result' in st.session_state and st.session_state.experiment_result:
                experiment_result = st.session_state.experiment_result
                
                # Display experiment results
                st.markdown("### 📊 Experiment Results")
                st.markdown(f"**Model**: {experiment_result.get('model_name', 'Unknown')}")
                
                task_type = experiment_result.get('task_type') or experiment_result.get('experiment_task_type')
                if task_type:
                    st.markdown(f"**Task Type**: {task_type}")
                else:
                    st.markdown("**Task Type**: Unknown")
                
                message = experiment_result.get('message') or experiment_result.get('error', 'No message available')
                st.markdown(f"**Message**: {message}")
                
                timestamp = experiment_result.get('timestamp') or experiment_result.get('experiment_timestamp', 'Unknown')
                st.markdown(f"**Timestamp**: {timestamp}")
                
                # Display basic visualizations if available
                if 'visualizations' in experiment_result and experiment_result['visualizations']:
                    st.markdown("### 📈 Visualizations")
                    for viz in experiment_result['visualizations']:
                        if viz.get('type') == 'figure':
                            st.pyplot(viz['data'])
                        elif viz.get('type') == 'plot':
                            st.plotly_chart(viz['data'])
                        elif viz.get('type') == 'image':
                            st.image(viz['data'])
                
                # Display detailed results
                if 'detailed_results' in experiment_result:
                    st.markdown("### 📋 Detailed Results")
                    st.json(experiment_result['detailed_results'])
                
                # Clear the experiment result after display
                del st.session_state.experiment_result
            elif is_knowledge_command:
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
                        
                        # Separate regular analysis figures from cobra visual figures
                        regular_figures = []
                        cobra_visual_figures = []
                        
                        for figure_data in figures:
                            if isinstance(figure_data, dict):
                                title = figure_data.get('title', figure_data.get('name', ''))
                                if title.startswith('Cobra Visual -'):
                                    cobra_visual_figures.append(figure_data)
                                else:
                                    regular_figures.append(figure_data)
                            else:
                                regular_figures.append(figure_data)
                        
                        # Display regular analysis figures first
                        if regular_figures:
                            st.markdown("#### 🔬 Basic Model Analysis")
                            for i, figure_data in enumerate(regular_figures):
                                if isinstance(figure_data, dict):
                                    # Handle dictionary format from new_model_analyzer_agent
                                    title = figure_data.get('title', figure_data.get('name', f'Figure {i+1}'))
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
                        
                        # Display cobra visual figures below regular analysis
                        if cobra_visual_figures:
                            st.markdown("---")
                            st.markdown("### 🎨 Cobra Visual Analysis (Fluxmap & Network Graphs)")
                            st.markdown("*Advanced metabolic network visualizations with flux data*")
                            
                            for i, figure_data in enumerate(cobra_visual_figures):
                                title = figure_data.get('title', figure_data.get('name', f'Cobra Visual Figure {i+1}'))
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
                        
                        # Clear the figures from session state
                        del st.session_state.current_figures
                
                # Display transition success message if available
                if 'transition_success_message' in st.session_state:
                    st.success(st.session_state.transition_success_message)
                    del st.session_state.transition_success_message
                
                # Display explanation error message if available
                if 'explanation_error_message' in st.session_state:
                    st.error(st.session_state.explanation_error_message)
                    del st.session_state.explanation_error_message
                
                # Display analysis cancelled message if available
                if 'analysis_cancelled_message' in st.session_state:
                    st.info(st.session_state.analysis_cancelled_message)
                    del st.session_state.analysis_cancelled_message
                
                # Display transition error message if available
                if 'transition_error_message' in st.session_state:
                    st.error(st.session_state.transition_error_message)
                    del st.session_state.transition_error_message
                
                # Display experiment transition success message if available
                if 'experiment_transition_success_message' in st.session_state:
                    st.success(st.session_state.experiment_transition_success_message)
                    del st.session_state.experiment_transition_success_message
                
                # Display experiment success message if available
                if 'experiment_success_message' in st.session_state:
                    st.success(st.session_state.experiment_success_message)
                    del st.session_state.experiment_success_message
                
                # Display experiment error message if available
                if 'experiment_error_message' in st.session_state:
                    st.error(st.session_state.experiment_error_message)
                    if 'experiment_error_traceback' in st.session_state:
                        with st.expander("Error Details"):
                            st.code(st.session_state.experiment_error_traceback)
                        del st.session_state.experiment_error_traceback
                    del st.session_state.experiment_error_message
                
                # Display experiment cancelled message if available
                if 'experiment_cancelled_message' in st.session_state:
                    st.info(st.session_state.experiment_cancelled_message)
                    del st.session_state.experiment_cancelled_message
                
                # Display experiment transition error message if available
                if 'experiment_transition_error_message' in st.session_state:
                    st.error(st.session_state.experiment_transition_error_message)
                    del st.session_state.experiment_transition_error_message
                
                # Note: analyse_success_message is now included in the result string
                
                # Display analyse warning message if available
                if 'analyse_warning_message' in st.session_state:
                    st.warning(st.session_state.analyse_warning_message)
                    del st.session_state.analyse_warning_message
                
                # Display next step explanation error message if available
                if 'next_step_explanation_error_message' in st.session_state:
                    st.error(st.session_state.next_step_explanation_error_message)
                    del st.session_state.next_step_explanation_error_message
                
                # Display next step model only message if available
                if 'next_step_model_only_message' in st.session_state:
                    st.info(st.session_state.next_step_model_only_message)
                    del st.session_state.next_step_model_only_message
                
                # Display next step task only message if available
                if 'next_step_task_only_message' in st.session_state:
                    st.info(st.session_state.next_step_task_only_message)
                    del st.session_state.next_step_task_only_message
                
                # Display next step complete config message if available
                if 'next_step_complete_config_message' in st.session_state:
                    st.info(st.session_state.next_step_complete_config_message)
                    del st.session_state.next_step_complete_config_message
                
                # Display next step analysis error message if available
                if 'next_step_analysis_error_message' in st.session_state:
                    st.error(st.session_state.next_step_analysis_error_message)
                    del st.session_state.next_step_analysis_error_message
                
                # Display no analysis type message if available
                if 'no_analysis_type_message' in st.session_state:
                    st.info(st.session_state.no_analysis_type_message)
                    del st.session_state.no_analysis_type_message
                
                # Display task pick warning message if available
                if 'task_pick_warning_message' in st.session_state:
                    st.warning(st.session_state.task_pick_warning_message)
                    del st.session_state.task_pick_warning_message
                
                # Display task pick error message if available
                if 'task_pick_error_message' in st.session_state:
                    st.error(st.session_state.task_pick_error_message)
                    del st.session_state.task_pick_error_message
                
                # Display continue processing message if available
                if 'continue_processing_message' in st.session_state:
                    st.info(st.session_state.continue_processing_message)
                    del st.session_state.continue_processing_message
                
                # Note: explanation_result and pending_prompt will be displayed outside of chat message display
                # to prevent them from being overwritten by new messages
                
                # Display experiment results if available
                if 'last_experiment_result' in st.session_state and st.session_state.last_experiment_result:
                    experiment_result = st.session_state.last_experiment_result
                    task_type = st.session_state.get('experiment_task_type', 2)
                    
                    st.markdown("---")
                    st.markdown("## 🔬 Experiment Results")
                    
                    if task_type == 1:  # FBA Analysis
                        # Use enhanced visualization for FBA results
                        result_visualizer = get_result_visualizer()
                        result_visualizer.visualize_fba_results(experiment_result)
                    elif task_type == 2:  # Gene deletion analysis
                        # Use enhanced visualization for gene deletion results (only once)
                        result_visualizer = get_result_visualizer()
                        result_visualizer.visualize_gene_deletion_results_enhanced(experiment_result)
                        
                        # Display enhanced LLM analysis if available
                        if 'gene_deletion_llm_analysis' in st.session_state:
                            st.markdown("## 🤖 Enhanced LLM Analysis")
                            st.markdown(st.session_state.gene_deletion_llm_analysis)
                    elif task_type == 6:  # Constraint-Based Analysis
                        # Use enhanced visualization for constraint-based analysis results
                        result_visualizer = get_result_visualizer()
                        result_visualizer.visualize_constraint_based_analysis_results(experiment_result)
                    
                    # Clear the experiment result after displaying
                    del st.session_state.last_experiment_result
                    if 'experiment_task_type' in st.session_state:
                        del st.session_state.experiment_task_type
                    if 'gene_deletion_llm_analysis' in st.session_state:
                        del st.session_state.gene_deletion_llm_analysis
                    if 'constraint_based_analysis_result' in st.session_state:
                        del st.session_state.constraint_based_analysis_result
                    if 'fba_analysis_result' in st.session_state:
                        del st.session_state.fba_analysis_result

        st.session_state.history.append({"role": "assistant", "content": result})

    # Clear explanation result and pending prompt after they have been included in the result
    if 'explanation_result' in st.session_state:
        del st.session_state.explanation_result
    if 'pending_prompt' in st.session_state:
        del st.session_state.pending_prompt

if __name__ == "__main__":
    main() 