import os
import asyncio
import sys
import warnings
from agent.code_writer import CodeWriterAgent
from agent.code_explainer import CodeExplainerAgent
from agent.code_debugger import CodeDebuggerAgent
from agent.code_executor import CodeExecutor
from agent.search_tool import SearchTool
from agent.rag_tool import RAGTool
from agent.memory import Memory
from agent.virtual_command_agent import VirtualCommandAgent
from agent.download_tool import DownloadTool
from agent.model_analyzer_agent import ModelAnalyzerAgent
from agent.literature_agent import LiteratureAgent
from agent.agent_for_agent import AgentForAgent
from bio_task import initialize_bio_task
from dotenv import load_dotenv
import re

# 抑制 asyncio 相关的警告
warnings.filterwarnings("ignore", category=ResourceWarning, message=".*unclosed event loop.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="asyncio")

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
    model_analyzer = ModelAnalyzerAgent()
    literature_agent = LiteratureAgent()
    agent_for_agent = AgentForAgent()

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
            return "The model was not found. Please try other models."

    def literature_query(temp_kb_id_and_query):
        """Query a temporary knowledge base created by literature agent."""
        if not temp_kb_id_and_query:
            return "Please specify knowledge base ID and query. Format: literature_query <kb_id> <query>"
        
        # Split the input to get kb_id and query
        parts = temp_kb_id_and_query.split(' ', 1)
        if len(parts) < 2:
            return "Please provide both knowledge base ID and query. Format: literature_query <kb_id> <query>"
        
        temp_kb_id = parts[0]
        query = parts[1]
        
        return literature_agent.query_knowledge_base(temp_kb_id, query)

    def list_literature_kbs():
        """List all available temporary knowledge bases."""
        return literature_agent.list_knowledge_bases()

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
        "literature": literature_agent.run,
        "literature_query": literature_query,
        "list_literature_kbs": list_literature_kbs,
        "search": search_and_answer,
        "update_data": lambda: rag_tool.update_knowledge_base(),
        "force_update": lambda: rag_tool.force_update_knowledge_base(),
        "models": show_models,
        "reset_temp_kb": lambda: literature_agent.reset_temporary_knowledge_base()
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
                    result = "The model was not found. Please try other models."
                    matched = True
                    special_command_executed = True
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
                            result += f"\nThe model was not found. Please try other models."
                        
                        matched = True
                    else:
                        result = "The model was not found. Please try other models."
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
        
        # Step 3.5: Agent for Agent - Check if input is related to biological research
        if not special_command_executed and not matched:
            # First check if user input already contains a regular command
            cmd_lower = user_input.lower().strip()
            contains_regular_command = False
            for cmd in regular_commands.keys():
                if cmd_lower.startswith(cmd):
                    contains_regular_command = True
                    break
            
            # If no regular command found, check biological relevance
            if not contains_regular_command:
                print("Agent for Agent: Checking biological relevance...", file=sys.stderr)
                agent_result = agent_for_agent.check_biological_relevance(user_input)
                
                if agent_result['is_relevant']:
                    print(f"Agent for Agent: Biological relevance detected (confidence: {agent_result['confidence']:.2f})", file=sys.stderr)
                    print(f"Agent for Agent: Reasoning: {agent_result['reasoning']}", file=sys.stderr)
                    print(f"Agent for Agent: Modified input: {agent_result['modified_input']}", file=sys.stderr)
                    
                    # Use the modified input for further processing
                    user_input = agent_result['modified_input']
                else:
                    print(f"Agent for Agent: Not biologically relevant (confidence: {agent_result['confidence']:.2f})", file=sys.stderr)
                    print(f"Agent for Agent: Reasoning: {agent_result['reasoning']}", file=sys.stderr)
        
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
    # 设置事件循环以修复 "unclosed event loop" 错误
    loop = None
    try:
        # 获取或创建事件循环
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            # 没有事件循环，创建新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 运行主程序
        main()
        
    except Exception as e:
        print(f"程序执行错误: {e}")
    finally:
        # 确保所有事件循环正确关闭
        try:
            # 关闭当前事件循环
            if loop and not loop.is_closed():
                # 关闭所有挂起的任务
                pending_tasks = asyncio.all_tasks(loop)
                if pending_tasks:
                    for task in pending_tasks:
                        task.cancel()
                    # 等待所有任务取消完成
                    loop.run_until_complete(asyncio.gather(*pending_tasks, return_exceptions=True))
                
                loop.close()
            
            # 尝试关闭其他可能的事件循环
            try:
                current_loop = asyncio.get_event_loop()
                if current_loop and not current_loop.is_closed() and current_loop != loop:
                    current_loop.close()
            except RuntimeError:
                pass  # 没有事件循环运行，忽略
                
        except Exception as e:
            print(f"关闭事件循环时出错: {e}")
        
        # 清理 asyncio 策略
        try:
            asyncio.set_event_loop(None)
        except Exception:
            pass 