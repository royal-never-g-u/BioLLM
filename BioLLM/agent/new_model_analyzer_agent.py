import os
import sys
import json
import numpy as np
from agent.base import BaseAgent
import warnings
warnings.filterwarnings('ignore')

class NewModelAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        # Get the correct path to downloads directory
        # Handle different running environments (CLI, Streamlit, etc.)
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_file_dir)  # BioLLM directory
        
        possible_paths = [
            os.path.join(project_root, "downloads"),     # From BioLLM/agent/
            os.path.join(os.path.dirname(project_root), "downloads"),  # From BioLLM/BioLLM/
            "../downloads",                              # From BioLLM/BioLLM/
            "../../downloads",                           # From BioLLM/agent/
            "downloads",                                 # From project root
            "./downloads",                               # From current directory
        ]
        
        self.downloads_dir = None
        for path in possible_paths:
            if os.path.exists(path):
                # Verify this is the correct downloads directory by checking for .mat files
                try:
                    files = os.listdir(path)
                    if any(f.endswith('.mat') for f in files):
                        self.downloads_dir = path
                        break
                except:
                    continue
        
        if self.downloads_dir is None:
            # Fallback to relative path
            self.downloads_dir = "../downloads"
        
        # Print downloads directory contents during initialization
        print(f"📁 Downloads directory: {self.downloads_dir}")
        if os.path.exists(self.downloads_dir):
            print("📋 Files in downloads directory:")
            try:
                files = os.listdir(self.downloads_dir)
                if files:
                    for i, file in enumerate(sorted(files), 1):
                        file_path = os.path.join(self.downloads_dir, file)
                        file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
                        file_type = "📄" if file.endswith('.mat') else "📁"
                        print(f"  {i}. {file_type} {file} ({file_size:,} bytes)")
                else:
                    print("  (empty directory)")
            except Exception as e:
                print(f"  ❌ Error reading directory: {e}")
        else:
            print("  ❌ Downloads directory not found")
        
        self.available_models = self._scan_downloads_directory()
        
        # Initialize figures storage for Streamlit display
        self.current_figures = []
        self.streamlit_figures = []
        
        print(f"🔬 Available .mat models: {len(self.available_models)}")
        for i, model in enumerate(self.available_models, 1):
            model_name = os.path.basename(model).replace('.mat', '')
            print(f"  {i}. {model_name}")
        print()
    
    def _scan_downloads_directory(self):
        """
        Dynamically scan the downloads directory for .mat files
        """
        available_models = []
        if os.path.exists(self.downloads_dir):
            for file in os.listdir(self.downloads_dir):
                if file.endswith('.mat'):
                    model_path = os.path.join(self.downloads_dir, file)
                    available_models.append(model_path)
        return available_models
    
    def run(self, prompt: str, memory=None) -> str:
        """
        Analyze COBRA models and provide detailed information about metabolites, reactions, and genes
        
        Args:
            prompt (str): User input containing model name or analysis request
            memory: Memory object (not used in this agent)
        
        Returns:
            str: Analysis results and visualizations
        """
        try:
            # Clear previous figures at the start of each analysis
            self.current_figures = []
            self.streamlit_figures = []
            
            # Extract model name from prompt - use the same method as match_command
            model_name = self._extract_model_name_from_biosimulation_models(prompt)
            
            if not model_name:
                # Clear figures when no model name is found
                self.current_figures = []
                self.streamlit_figures = []
                return self._list_available_models()
            
            # Find the model file
            model_file = self._find_model_file(model_name)
            if not model_file:
                # Clear figures when model file is not found
                self.current_figures = []
                self.streamlit_figures = []
                return f"❌ Model '{model_name}' not found. Available models:\n{self._list_available_models()}"
            
            # TODO: Implement actual model analysis
            # For now, return a placeholder message
            return self._placeholder_analysis(model_file, model_name)
            
        except Exception as e:
            return f"❌ Error during model analysis: {str(e)}"
    
    def match_command(self, user_input: str) -> dict:
        """
        Match user input to analyse command
        
        Args:
            user_input (str): User input to match
            
        Returns:
            dict: Match result with confidence and reasoning
        """
        user_input_lower = user_input.lower()
        
        # Check for analyse-related keywords
        analyse_keywords = [
            'analyse', 'analyze', 'analysis', 'analyze model', 'analyse model',
            'model analysis', 'metabolic model', 'cobra model', 'metabolic network',
            'metabolites', 'reactions', 'genes', 'metabolic', 'biomass'
        ]
        
        # Check if input contains analyse keywords
        keyword_match = any(keyword in user_input_lower for keyword in analyse_keywords)
        
        if keyword_match:
            # Check for model names in BiosimulationModels.txt
            model_name = self._extract_model_name_from_biosimulation_models(user_input)
            
            if model_name:
                return {
                    'matched': True,
                    'command_name': 'analyse',
                    'confidence': 0.9,
                    'reasoning': f'Detected analyse command with model "{model_name}"',
                    'model_name': model_name
                }
            else:
                return {
                    'matched': True,
                    'command_name': 'analyse',
                    'confidence': 0.7,
                    'reasoning': 'Detected analyse command but no specific model found',
                    'model_name': None
                }
        
        return {
            'matched': False,
            'command_name': None,
            'confidence': 0.0,
            'reasoning': 'No analyse command detected'
        }
    
    def _extract_model_name(self, prompt: str) -> str:
        """
        Extract model name from user prompt by matching against available .mat files
        """
        if prompt is None:
            return None
            
        prompt_lower = prompt.lower()
        
        # Get available model names from .mat files
        available_model_names = []
        for model_file in self.available_models:
            if os.path.exists(model_file):
                model_name = os.path.basename(model_file).replace('.mat', '')
                available_model_names.append(model_name)
        
        # Try to match user input against available model names
        for model_name in available_model_names:
            # Check for exact match (case insensitive)
            if model_name.lower() in prompt_lower:
                return model_name
            
            # Check for partial matches (e.g., "imm904" matches "iMM904")
            if model_name.lower().replace('_', '').replace('-', '') in prompt_lower.replace('_', '').replace('-', ''):
                return model_name
        
        return None
    
    def _extract_model_name_from_biosimulation_models(self, user_input: str) -> str:
        """
        Extract model name from user input by matching against BiosimulationModels.txt
        
        Args:
            user_input (str): User input to search for model names
            
        Returns:
            str: Matched model name or None
        """
        if user_input is None:
            return None
            
        try:
            # Read BiosimulationModels.txt
            models_file = "BiosimulationModels.txt"
            if not os.path.exists(models_file):
                return None
            
            with open(models_file, 'r', encoding='utf-8') as f:
                model_names = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            user_input_lower = user_input.lower()
            
            # First, try exact word matches
            user_words = user_input_lower.split()
            for word in user_words:
                if word in [name.lower() for name in model_names]:
                    # Find the original case version
                    for model_name in model_names:
                        if model_name.lower() == word:
                            return model_name
            
            # If no exact match, try partial matches
            for model_name in model_names:
                if model_name.lower() in user_input_lower:
                    return model_name
            
            return None
            
        except Exception as e:
            print(f"Warning: Error reading BiosimulationModels.txt: {e}")
            return None
    
    def _find_model_file(self, model_name: str) -> str:
        """
        Find the actual model file path by matching model name
        """
        if model_name is None:
            return None
            
        # Refresh available models
        self.available_models = self._scan_downloads_directory()
        
        for model_file in self.available_models:
            file_model_name = os.path.basename(model_file).replace('.mat', '')
            if model_name.lower() == file_model_name.lower():
                if os.path.exists(model_file):
                    return model_file
        return None
    
    def _list_available_models(self) -> str:
        """
        List all available models found in downloads directory
        """
        result = "📋 Available Models:\n"
        result += "=" * 30 + "\n"
        
        # Refresh available models
        self.available_models = self._scan_downloads_directory()
        
        if not self.available_models:
            result += "  No .mat files found in downloads directory.\n"
            result += "  Please download models first using the download command.\n"
        else:
            for i, model_file in enumerate(self.available_models, 1):
                model_name = os.path.basename(model_file).replace('.mat', '')
                result += f"  {i}. {model_name}\n"
        
        result += "\n💡 Usage: analyse [model_name]\n"
        result += "   Example: analyse e_coli_core\n"
        return result
    
    def _placeholder_analysis(self, model_file: str, model_name: str) -> str:
        """
        Implement model analysis using the metabolic_model_analyzer_template
        
        Args:
            model_file (str): Path to the model file
            model_name (str): Name of the model
            
        Returns:
            str: Analysis results with text and visualizations
        """
        try:
            print(f"🔬 Starting analysis for model: {model_name}")
            print(f"📁 Model file: {model_file}")
            
            # Step 1: Create a temporary analysis script with model path inserted
            analysis_script = self._create_analysis_script(model_file, model_name)
            
            # Step 2: Call executor agent to run the analysis script
            executor_result = self._run_analysis_with_executor(analysis_script)
            
            # Step 3: Analyze the results with LLM
            analysis_report = self._analyze_results_with_llm(model_name, executor_result)
            
            # Step 4: Generate visualizations and final output
            final_output = self._generate_final_output(model_name, analysis_report, executor_result)
            
            return final_output
            
        except Exception as e:
            error_msg = f"❌ Error during model analysis: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _create_analysis_script(self, model_file: str, model_name: str) -> str:
        """
        Create a temporary analysis script by inserting model path into template
        
        Args:
            model_file (str): Path to the model file
            model_name (str): Name of the model
            
        Returns:
            str: Path to the created analysis script
        """
        try:
            # Read the template file
            template_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'CodeTemplate', 'ModelAnalyse', 'metabolic_model_analyzer_template.py'
            )
            
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"Template file not found: {template_path}")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Replace the slot values with actual model information
            # Convert .mat file path to appropriate format for the template
            model_path = model_file
            
            # Create a temporary script with the model path inserted
            analysis_script_content = template_content.replace(
                'SLOT_MODEL_PATH = "downloads/your_model_file.xml"',
                f'SLOT_MODEL_PATH = "{model_path}"'
            ).replace(
                'SLOT_OUTPUT_DIR = "analysis_results"',
                f'SLOT_OUTPUT_DIR = "analysis_results/{model_name}"'
            ).replace(
                'SLOT_MODEL_NAME = "Your Model Name"',
                f'SLOT_MODEL_NAME = "{model_name}"'
            )
            
            # Create temporary script file
            temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            script_filename = f"{model_name}_analysis_script.py"
            script_path = os.path.join(temp_dir, script_filename)
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(analysis_script_content)
            
            print(f"✅ Created analysis script: {script_path}")
            return script_path
            
        except Exception as e:
            raise Exception(f"Error creating analysis script: {str(e)}")
    
    def _run_analysis_with_executor(self, script_path: str) -> str:
        """
        Run the analysis script using the executor agent
        
        Args:
            script_path (str): Path to the analysis script
            
        Returns:
            str: Execution results
        """
        try:
            # Create a temporary file to trigger executor
            temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Create a trigger file that executor will use
            trigger_filename = "analysis_trigger"
            trigger_py_path = os.path.join(temp_dir, f"{trigger_filename}.py")
            trigger_txt_path = os.path.join(temp_dir, f"{trigger_filename}.txt")
            
            # Create the Python trigger file that will run our analysis script
            trigger_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysis trigger script
"""

import subprocess
import sys
import os

def main():
    """Run the analysis script"""
    script_path = "{script_path}"
    
    if os.path.exists(script_path):
        print(f"🔬 Running analysis script: {{script_path}}")
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            print("📋 Analysis Results:")
            print("=" * 50)
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Errors/Warnings:")
                print(result.stderr)
                
        except subprocess.TimeoutExpired:
            print("⏰ Analysis timed out after 5 minutes")
        except Exception as e:
            print(f"❌ Error running analysis: {{e}}")
    else:
        print(f"❌ Analysis script not found: {{script_path}}")

if __name__ == "__main__":
    main()
'''
            
            with open(trigger_py_path, 'w', encoding='utf-8') as f:
                f.write(trigger_content)
            
            # Create a simple bash command file
            with open(trigger_txt_path, 'w', encoding='utf-8') as f:
                f.write(f"echo 'Starting analysis for {os.path.basename(script_path)}'")
            
            # Copy these files to ResultsData so executor can find them
            results_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ResultsData')
            os.makedirs(results_data_dir, exist_ok=True)
            
            import shutil
            shutil.copy2(trigger_py_path, os.path.join(results_data_dir, f"{trigger_filename}.py"))
            shutil.copy2(trigger_txt_path, os.path.join(results_data_dir, f"{trigger_filename}.txt"))
            
            # Import and use the executor agent
            from agent.code_executor import CodeExecutor
            executor = CodeExecutor()
            
            print(f"🚀 Running analysis with executor...")
            result = executor.run(trigger_filename)
            
            print(f"✅ Analysis completed")
            return result
            
        except Exception as e:
            raise Exception(f"Error running analysis with executor: {str(e)}")
    
    def _analyze_results_with_llm(self, model_name: str, executor_result: str) -> str:
        """
        Analyze the executor results with LLM to generate insights
        
        Args:
            model_name (str): Name of the model
            executor_result (str): Results from executor
            
        Returns:
            str: LLM-generated analysis report
        """
        try:
            # Create a prompt for LLM analysis
            analysis_prompt = f"""
You are a metabolic model analysis expert. Analyze the following results from a COBRA metabolic model analysis and provide comprehensive insights.

Model Name: {model_name}

Analysis Results:
{executor_result}

Please provide a detailed analysis including:

1. **Model Overview**: Basic statistics and characteristics
2. **Metabolic Network Structure**: Key pathways and reactions
3. **Metabolites Analysis**: Important metabolites and their roles
4. **Reactions Analysis**: Key reactions and their significance
5. **Genes Analysis**: Important genes and their functions
6. **Pathway Distribution**: Major metabolic pathways
7. **Biological Insights**: What this tells us about the organism
8. **Potential Applications**: How this model could be used

Format your response with clear sections, bullet points, and insights that would be valuable for researchers and students.

Focus on making the analysis accessible and informative, highlighting the most important findings from the data.
"""

            # Call LLM for analysis
            from agent.code_writer import CodeWriterAgent
            llm_agent = CodeWriterAgent()
            
            print(f"🤖 Analyzing results with LLM...")
            analysis_report = llm_agent.chat(analysis_prompt)
            
            return analysis_report
            
        except Exception as e:
            raise Exception(f"Error analyzing results with LLM: {str(e)}")
    
    def _generate_final_output(self, model_name: str, analysis_report: str, executor_result: str) -> str:
        """
        Generate the final output with text and visualization information
        
        Args:
            model_name (str): Name of the model
            analysis_report (str): LLM-generated analysis report
            executor_result (str): Original executor results
            
        Returns:
            str: Final formatted output
        """
        try:
            # Create the final output
            output = f"🔬 Metabolic Model Analysis Report\n"
            output += f"Model: {model_name}\n"
            output += "=" * 60 + "\n\n"
            
            # Add LLM analysis
            output += "📊 AI-Generated Analysis\n"
            output += "-" * 30 + "\n"
            output += analysis_report
            output += "\n\n"
            
            # Add technical details
            output += "🔧 Technical Details\n"
            output += "-" * 30 + "\n"
            output += "Raw analysis results and generated files:\n\n"
            
            # Extract file paths from executor result
            import re
            file_patterns = [
                r'saved to: ([^\n]+)',
                r'Saved to: ([^\n]+)',
                r'File saved to: ([^\n]+)'
            ]
            
            generated_files = []
            for pattern in file_patterns:
                matches = re.findall(pattern, executor_result)
                generated_files.extend(matches)
            
            if generated_files:
                output += "📁 Generated Files:\n"
                for i, file_path in enumerate(generated_files, 1):
                    output += f"  {i}. {file_path}\n"
                output += "\n"
            
            # Add visualization information
            output += "📈 Visualizations\n"
            output += "-" * 30 + "\n"
            
            # Check for generated visualization files
            analysis_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analysis_results', model_name)
            if os.path.exists(analysis_dir):
                vis_files = [f for f in os.listdir(analysis_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.svg', '.pdf'))]
                if vis_files:
                    output += "Generated visualization files:\n"
                    for i, vis_file in enumerate(vis_files, 1):
                        output += f"  {i}. {vis_file}\n"
                else:
                    output += "No visualization files found.\n"
            else:
                output += "Analysis directory not found.\n"
            
            output += "\n"
            
            # Add usage instructions
            output += "💡 Usage Instructions\n"
            output += "-" * 30 + "\n"
            output += "• View generated files in the analysis_results directory\n"
            output += "• Check the Temp directory for intermediate files\n"
            output += "• Use the visualization files for presentations and reports\n"
            output += "• The analysis report provides biological insights and applications\n\n"
            
            # Store figures for Streamlit display
            self._prepare_streamlit_figures(model_name)
            
            return output
            
        except Exception as e:
            raise Exception(f"Error generating final output: {str(e)}")
    
    def _prepare_streamlit_figures(self, model_name: str):
        """
        Prepare figures for Streamlit display
        
        Args:
            model_name (str): Name of the model
        """
        try:
            # Look for generated visualization files
            analysis_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analysis_results', model_name)
            
            if os.path.exists(analysis_dir):
                vis_files = [f for f in os.listdir(analysis_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.svg', '.pdf'))]
                
                # Store file paths for Streamlit
                self.current_figures = []
                for vis_file in vis_files:
                    file_path = os.path.join(analysis_dir, vis_file)
                    self.current_figures.append({
                        'name': vis_file,
                        'path': file_path,
                        'type': 'image'
                    })
                
                # Also look for HTML reports
                html_files = [f for f in os.listdir(analysis_dir) if f.endswith('.html')]
                for html_file in html_files:
                    file_path = os.path.join(analysis_dir, html_file)
                    self.current_figures.append({
                        'name': html_file,
                        'path': file_path,
                        'type': 'html'
                    })
                
                print(f"📊 Prepared {len(self.current_figures)} figures for Streamlit display")
            else:
                self.current_figures = []
                print("📊 No analysis directory found for figures")
                
        except Exception as e:
            print(f"⚠️ Error preparing Streamlit figures: {e}")
            self.current_figures = []
    
    def chat(self, prompt: str, memory=None) -> str:
        """
        Chat interface for model analysis
        """
        return self.run(prompt, memory)
