import os
from agent.code_writer import CodeWriterAgent
from agent.code_explainer import CodeExplainerAgent
from agent.code_debugger import CodeDebuggerAgent
from agent.code_executor import CodeExecutor
from agent.search_tool import SearchTool
from agent.rag_tool import RAGTool
from agent.memory import Memory
from agent.virtual_command_agent import VirtualCommandAgent
from agent.download_tool import DownloadTool
from agent.new_model_analyzer_agent import NewModelAnalyzerAgent
from bio_task import initialize_bio_task
from dotenv import load_dotenv
import re

load_dotenv()

def strip_command(user_input, command):
    # Remove command keywords at the beginning and subsequent spaces
    if user_input is None:
        return ""
    pattern = rf"^{re.escape(command)}[\s:：]*"
    return re.sub(pattern, '', user_input, flags=re.IGNORECASE).strip()

def extract_model_name(user_input, available_models):
    """
    Extract biosimulation model name from user input.
    Returns the matched model name or None if no match found.
    """
    if user_input is None:
        return None
    user_input_lower = user_input.lower()
    
    # First, try exact word matches
    user_words = user_input_lower.split()
    for word in user_words:
        if word in available_models:
            return word
    
    # If no exact match, try partial matches (for cases like "e_coli_core model")
    for model in available_models:
        if model.lower() in user_input_lower:
            return model
    
    return None

def main(initialize_only=False, initialize_bio_task_flag=True):
    # Initialize BioTask file only when explicitly requested (usually on app startup)
    if initialize_bio_task_flag:
        initialize_bio_task()
    
    memory = Memory()
    code_writer = CodeWriterAgent()
    code_explainer = CodeExplainerAgent()
    code_debugger = CodeDebuggerAgent()
    code_executor = CodeExecutor()
    search_tool = SearchTool()
    rag_tool = RAGTool()
    virtual_command_agent = VirtualCommandAgent()
    download_tool = DownloadTool()
    model_analyzer = NewModelAnalyzerAgent()

    def search_and_answer(prompt):
        search_results = search_tool.run(prompt)
        answer_prompt = f"Based on the following search results, please provide a comprehensive answer to the user's question.\n\nSearch Results:\n{search_results}\n\nUser Question: {prompt}"
        return code_writer.chat(answer_prompt)

    def show_models():
        """Show available biosimulation models."""
        models = rag_tool.get_saved_biosimulation_models()
        if models:
            return f"Available biosimulation models:\n{', '.join(models)}"
        else:
            return "No models found. Run 'update_data' or 'force_update' to extract models from papers."

    def download_model(model_name):
        """Download a specific model from BIGG database."""
        if not model_name:
            return "Please specify a model name to download."
        
        result = download_tool.download_model_from_name(model_name)
        if result['success']:
            return f"✓ {result['message']}\nFile saved to: {result['file_path']}"
        else:
            return f"✗ Download failed: {result['message']}"

    # Group 1: Special commands that need virtual command recognition and BiosimulationModels
    special_commands = {
        "download": download_model,
        "analyse": model_analyzer.run
    }
    
    # Group 2: Regular commands
    regular_commands = {
        "generate": code_writer.run,
        "explain": code_explainer.run,
        "debug": code_debugger.run,
        "execute": code_executor.run,
        "knowledge": rag_tool.run,
        "search": search_and_answer,
        "update_data": lambda: rag_tool.update_knowledge_base(),
        "force_update": lambda: rag_tool.force_update_knowledge_base(),
        "models": show_models
    }
    
    # Combined commands for help display
    commands = {**regular_commands, **special_commands}
    

    
    if initialize_only:
        return memory, commands

    print("Welcome to the BioLLM AI Agent (supports Python/Matlab, type 'help' to see functions)")
    while True:
        user_input = input("\nUser: ")
        if user_input.strip().lower() in ["exit", "quit"]:
            break
        
        if user_input.strip().lower() == 'help':
            print("\nAvailable commands: " + ", ".join(list(commands.keys())))
            print("\nCommand Groups:")
            print("📦 Special Commands (with virtual command recognition):")
            print("  - download: Download biosimulation models (supports: download, get, fetch, obtain, retrieve)")
            print("  - analyse: Analyze COBRA models (supports: analyze, analyse, analysis, examine, study, investigate)")
            print("\n🛠️ Regular Commands:")
            print("  - generate, explain, debug, execute, knowledge, search, update_data, force_update, models")
            print("\nVirtual commands:")
            print("- choose model: Use phrases like 'choose a model', 'select model', 'pick model' to select biosimulation models")
            print("- analyse model: Use phrases like 'analyze model', 'metabolic analysis', 'COBRA analysis' to analyze models")
            print("\nFallback mechanism:")
            print("- If special commands fail or don't match, system falls back to regular commands")
            print("- If no commands match, system uses default chat")
            continue

        matched = False
        result = ""
        
        # Check for virtual command matches
        virtual_match = virtual_command_agent.match_command(user_input)
        
        # Check for analyse command matches
        analyse_match = model_analyzer.match_command(user_input)
        
        # Print debug info to stderr for command line users
        import sys
        if virtual_match['matched']:
            print(f"Virtual Command Detected: {virtual_match['command_name']} (confidence: {virtual_match['confidence']:.2f})", file=sys.stderr)
            print(f"Reasoning: {virtual_match['reasoning']}", file=sys.stderr)
        
        if analyse_match['matched']:
            print(f"Analyse Command Detected: {analyse_match['command_name']} (confidence: {analyse_match['confidence']:.2f})", file=sys.stderr)
            print(f"Reasoning: {analyse_match['reasoning']}", file=sys.stderr)
        
        # Step 1: Try special commands (download and analyse) with virtual command recognition
        special_command_executed = False
        
        # Check if user input contains virtual commands related to download or analyse
        download_virtual_keywords = ['download', 'get', 'fetch', 'obtain', 'retrieve']
        analyse_virtual_keywords = ['analyze', 'analyse', 'analysis', 'examine', 'study', 'investigate']
        
        user_input_lower = user_input.lower()
        
        # Check for download virtual command
        if any(keyword in user_input_lower for keyword in download_virtual_keywords):
            print("Download virtual command detected, attempting download...", file=sys.stderr)
            try:
                # Extract model name from user input
                common_models = ['e_coli_core', 'iMM904', 'iND750', 'Recon1', 'Recon2', 'Recon3D']
                found_model = None
                for model in common_models:
                    if model.lower() in user_input_lower:
                        found_model = model
                        break
                
                if found_model:
                    print(f"Model found: {found_model}, executing download...", file=sys.stderr)
                    result = download_model(found_model)
                    matched = True
                    special_command_executed = True
                else:
                    print("No specific model found for download", file=sys.stderr)
            except Exception as e:
                print(f"Download command failed: {e}", file=sys.stderr)
        
        # Check for analyse virtual command
        # if not special_command_executed and any(keyword in user_input_lower for keyword in analyse_virtual_keywords):
        #     print("Analyse virtual command detected, attempting analysis...", file=sys.stderr)
        #     try:
        #         # Extract model name from user input
        #         common_models = ['e_coli_core', 'iMM904', 'iND750', 'Recon1', 'Recon2', 'Recon3D']
        #         found_model = None
        #         for model in common_models:
        #             if model.lower() in user_input_lower:
        #                 found_model = model
        #                 break
        #         
        #         if found_model:
        #             print(f"Model found: {found_model}, executing analysis...", file=sys.stderr)
        #             # Check if model file exists
        #             model_file = f"../downloads/{found_model}.mat"
        #             if os.path.exists(model_file):
        #                 result = model_analyzer.run(f"analyse {found_model}")
        #             else:
        #                 result = f"❌ Model file '{found_model}.mat' not found in downloads directory.\n\nPlease download the model first using:\ndownload {found_model}"
        #             matched = True
        #             special_command_executed = True
        #         else:
        #             print("No specific model found for analysis", file=sys.stderr)
        #     except Exception as e:
        #         print(f"Analyse command failed: {e}", file=sys.stderr)
        
        # Step 2: Handle virtual commands (if special commands didn't execute)
        if not special_command_executed and virtual_match['matched'] and virtual_match['confidence'] >= 0.1:
            command_name = virtual_match['command_name']
            
            # Handle choose_model virtual command
            if command_name == 'choose_model':
                # Get available biosimulation models
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
                        import sys
                        print(f"Attempting to download {found_model}.mat from BIGG database...", file=sys.stderr)
                        download_result = download_tool.download_model_from_name(found_model)
                        
                        if download_result['success']:
                            result += f"\n✓ {download_result['message']}"
                            result += f"\nFile saved to: {download_result['file_path']}"
                        else:
                            result += f"\n✗ Download failed: {download_result['message']}"
                        
                        matched = True
                    else:
                        result = f"No matching model found in your input. Available models: {', '.join(available_models)}\n\nPlease specify one of these models in your request."
                        matched = True
            
            # Handle analyse_model virtual command
            elif command_name == 'analyse_model':
                # Skip directly, do nothing, let subsequent fallback mechanism take effect
                pass
            
            # Handle other virtual commands here if needed
            else:
                result = f"Virtual command '{command_name}' detected but not implemented yet."
                matched = True
        
        # Step 3: Handle analyse commands (if virtual commands didn't execute)
        if not special_command_executed and not matched and analyse_match['matched'] and analyse_match['confidence'] >= 0.1:
            command_name = analyse_match['command_name']
            
            if command_name == 'analyse':
                model_name = analyse_match.get('model_name')
                
                if model_name:
                    # Check if model file exists
                    model_file = f"../downloads/{model_name}.mat"
                    if os.path.exists(model_file):
                        result = model_analyzer.run(f"analyse {model_name}")
                    else:
                        result = f"❌ Model file '{model_name}.mat' not found in downloads directory.\n\nPlease download the model first using:\ndownload {model_name}"
                else:
                    # No specific model found, show available models
                    result = model_analyzer.run("analyse")
                
                matched = True
        
        # Step 4: Fallback to regular commands (if special commands failed or didn't match)
        if not matched:
            cmd_lower = user_input.lower().strip()
            
            matched_cmd = None
            for cmd in regular_commands.keys():
                if cmd_lower.startswith(cmd):
                    matched_cmd = cmd
                    break

            if matched_cmd:
                if matched_cmd in ["update_data", "force_update"]: # No-prompt commands
                    result = regular_commands[matched_cmd]()
                else: # Commands with a prompt
                    prompt = strip_command(user_input, matched_cmd)
                    result = regular_commands[matched_cmd](prompt)
                    
                    # Check if it's executor's debug exit
                    if matched_cmd == "execute" and result and "[DEBUG_EXIT]" in result:
                        # Remove debug exit marker
                        result = result.replace("[DEBUG_EXIT]", "").strip()
                        matched = True
                        # Continue execution, let result display normally
                    else:
                        matched = True
        
        # Step 5: Final fallback to default chat
        if not matched:
            result = code_writer.chat(user_input, memory)

        # The print statement for the result seems to be missing in the previous version.
        # Let's ensure it is here.
        if result is not None:
            print(f"\nAI: {result}")
        memory.add(user_input, result)

if __name__ == "__main__":
    main() 