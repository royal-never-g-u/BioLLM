import os
import sys
import json
import numpy as np
from agent.base import BaseAgent
import warnings
warnings.filterwarnings('ignore')

# Import cobra visual agent
try:
    from agent.cobra_visual_agent import CobraVisualAgent
    COBRA_VISUAL_AVAILABLE = True
except ImportError:
    COBRA_VISUAL_AVAILABLE = False
    print("⚠️ CobraVisualAgent not available. Install required dependencies.")

class ModelAnalyzerAgent(BaseAgent):
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
        
        # Initialize cobra visual agent if available
        self.cobra_visual_agent = None
        if COBRA_VISUAL_AVAILABLE:
            try:
                self.cobra_visual_agent = CobraVisualAgent()
                print("✅ CobraVisualAgent initialized successfully")
            except Exception as e:
                print(f"⚠️ Failed to initialize CobraVisualAgent: {e}")
                self.cobra_visual_agent = None
        
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
            
            # Analyze the model
            return self._analyze_model(model_file, model_name)
            
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
    
    def _analyze_model(self, model_file: str, model_name: str) -> str:
        """
        Analyze a specific model and return detailed information
        """
        try:
            # Try to load with scipy first (basic analysis)
            import scipy.io
            model_data = scipy.io.loadmat(model_file)
            
            result = f"🔬 Metabolic Model Analysis Report\n"
            result += f"Model: {model_name}\n"
            result += "=" * 60 + "\n\n"
            
            # Basic structure analysis
            result += self._analyze_basic_structure(model_data, model_name)
            
            # Try COBRA analysis if available
            cobra_result = self._analyze_with_cobra(model_file, model_name)
            if cobra_result:
                result += "\n" + cobra_result
            
            # Analyze structured array data
            structured_result = self._analyze_structured_model(model_data, model_name)
            if structured_result:
                result += "\n" + structured_result
            
            # Generate AI-powered analysis insights
            ai_analysis = self._generate_ai_analysis(model_name, model_data, cobra_result, structured_result)
            if ai_analysis:
                result += "\n" + ai_analysis
            
            # Export data and get visualizations
            streamlit_figures = self._export_model_data(model_data, model_name)
            result += f"\n📁 Data exported to: model_data/{model_name}/"
            
            # Store figures for later use
            self.current_figures = streamlit_figures
            
            # Generate cobra visual analysis (fluxmap and network graphs)
            cobra_visual_result = self._generate_cobra_visual_analysis(model_file, model_name)
            if cobra_visual_result:
                result += "\n" + cobra_visual_result
            
            # Add technical details and usage instructions
            result += self._generate_technical_details(model_name)
            
            return result
            
        except Exception as e:
            import traceback
            return f"❌ Error analyzing model {model_name}: {str(e)}\n{traceback.format_exc()}"
    
    def _analyze_basic_structure(self, model_data: dict, model_name: str) -> str:
        """
        Analyze basic structure of the model data
        """
        result = "📊 Basic Model Structure:\n"
        result += "-" * 30 + "\n"
        
        matrices = []
        vectors = []
        scalars = []
        structured_arrays = []
        
        for key, data in model_data.items():
            if key.startswith('__'):
                continue
                
            if hasattr(data, 'shape'):
                if hasattr(data, 'dtype') and data.dtype.names:
                    # This is a structured array (metabolic model)
                    structured_arrays.append((key, data.shape, data.dtype.names))
                elif len(data.shape) == 1:
                    vectors.append((key, data.shape[0]))
                elif len(data.shape) == 2:
                    try:
                        sparsity = 1 - np.count_nonzero(data) / data.size if data.size > 0 else 0.0
                        matrices.append((key, data.shape, float(sparsity)))
                    except:
                        matrices.append((key, data.shape, 0.0))
                else:
                    scalars.append((key, data.shape))
            else:
                scalars.append((key, type(data).__name__))
        
        result += f"Total data objects: {len(matrices) + len(vectors) + len(scalars) + len(structured_arrays)}\n"
        result += f"Structured arrays: {len(structured_arrays)}\n"
        result += f"Matrices: {len(matrices)}\n"
        result += f"Vectors: {len(vectors)}\n"
        result += f"Scalars: {len(scalars)}\n\n"
        
        if structured_arrays:
            result += "🧬 Structured Arrays (Metabolic Models):\n"
            for name, shape, fields in structured_arrays:
                result += f"  - {name}: {shape} with fields: {', '.join(fields)}\n"
        
        if matrices:
            result += "\n📊 Matrices:\n"
            for name, shape, sparsity in matrices:
                result += f"  - {name}: {shape} ({sparsity:.2%} sparse)\n"
        
        if vectors:
            result += "\n📏 Vectors:\n"
            for name, size in vectors:
                result += f"  - {name}: {size} elements\n"
        
        if scalars:
            result += "\n🔢 Scalars:\n"
            for name, info in scalars:
                result += f"  - {name}: {info}\n"
        
        return result
    
    def _analyze_with_cobra(self, model_file: str, model_name: str) -> str:
        """
        Analyze model using COBRA framework
        """
        try:
            import cobra
            model = cobra.io.load_matlab_model(model_file)
            
            result = "\n🧬 COBRA Model Analysis:\n"
            result += "-" * 30 + "\n"
            
            # Basic statistics
            result += f"Metabolites: {len(model.metabolites)}\n"
            result += f"Reactions: {len(model.reactions)}\n"
            result += f"Genes: {len(model.genes)}\n\n"
            
            # Metabolites analysis
            result += "📊 Metabolites Analysis:\n"
            compartments = {}
            for met in model.metabolites:
                comp = met.compartment
                compartments[comp] = compartments.get(comp, 0) + 1
            
            for comp, count in compartments.items():
                result += f"  - {comp}: {count} metabolites\n"
            
            # Reactions analysis
            result += "\n⚡ Reactions Analysis:\n"
            reversible = len([r for r in model.reactions if r.reversibility])
            irreversible = len([r for r in model.reactions if not r.reversibility])
            result += f"  - Reversible: {reversible}\n"
            result += f"  - Irreversible: {irreversible}\n"
            
            # Genes analysis
            result += "\n🧬 Genes Analysis:\n"
            functional_genes = len([g for g in model.genes if g.functional])
            result += f"  - Functional: {functional_genes}\n"
            result += f"  - Non-functional: {len(model.genes) - functional_genes}\n"
            
            # Top metabolites by connectivity
            result += "\n🔗 Top 10 Metabolites by Connectivity:\n"
            met_connectivity = [(met.id, len(met.reactions)) for met in model.metabolites]
            met_connectivity.sort(key=lambda x: x[1], reverse=True)
            for i, (met_id, connectivity) in enumerate(met_connectivity[:10], 1):
                result += f"  {i}. {met_id}: {connectivity} reactions\n"
            
            # Top reactions by metabolites
            result += "\n🔗 Top 10 Reactions by Metabolite Count:\n"
            reaction_complexity = [(r.id, len(r.metabolites)) for r in model.reactions]
            reaction_complexity.sort(key=lambda x: x[1], reverse=True)
            for i, (rxn_id, complexity) in enumerate(reaction_complexity[:10], 1):
                result += f"  {i}. {rxn_id}: {complexity} metabolites\n"
            
            return result
            
        except ImportError:
            return "\n⚠️ COBRA not available. Install with: pip install cobra\n"
        except Exception as e:
            return f"\n⚠️ COBRA analysis failed: {str(e)}\n"
    
    def _analyze_structured_model(self, model_data: dict, model_name: str) -> str:
        """
        Analyze structured array metabolic model data
        """
        try:
            # Find the structured array (metabolic model)
            structured_model = None
            for key, data in model_data.items():
                if key.startswith('__'):
                    continue
                if hasattr(data, 'dtype') and data.dtype.names:
                    structured_model = data
                    break
            
            if structured_model is None:
                return ""
            
            result = "\n🧬 Structured Model Analysis:\n"
            result += "-" * 30 + "\n"
            
            # Get the first (and only) element of the structured array
            model_info = structured_model[0, 0]
            
            # Extract different components
            metabolites = model_info['mets'] if 'mets' in model_info.dtype.names else None
            reactions = model_info['rxns'] if 'rxns' in model_info.dtype.names else None
            genes = model_info['genes'] if 'genes' in model_info.dtype.names else None
            stoichiometry = model_info['S'] if 'S' in model_info.dtype.names else None
            
            if metabolites is not None:
                result += f"📊 Metabolites: {metabolites.shape[0]}\n"
                if metabolites.shape[0] <= 10:
                    result += f"  Sample metabolites: {[m[0] for m in metabolites[:5]]}\n"
            
            if reactions is not None:
                result += f"⚡ Reactions: {reactions.shape[0]}\n"
                if reactions.shape[0] <= 10:
                    result += f"  Sample reactions: {[r[0] for r in reactions[:5]]}\n"
            
            if genes is not None:
                result += f"🧬 Genes: {genes.shape[0]}\n"
                if genes.shape[0] <= 10:
                    result += f"  Sample genes: {[g[0] for g in genes[:5]]}\n"
            
            if stoichiometry is not None:
                result += f"🔗 Stoichiometry matrix: {stoichiometry.shape}\n"
                if hasattr(stoichiometry, 'nnz'):
                    result += f"  Non-zero elements: {stoichiometry.nnz}\n"
            
            # Analyze compartments if available
            if metabolites is not None:
                compartments = set()
                for met in metabolites:
                    met_id = met[0]
                    if '_' in met_id:
                        comp = met_id.split('_')[-1]
                        compartments.add(comp)
                
                if compartments:
                    result += f"🏠 Compartments: {', '.join(sorted(compartments))}\n"
            
            return result
            
        except Exception as e:
            return f"\n⚠️ Structured model analysis failed: {str(e)}\n"
    
    def _export_model_data(self, model_data: dict, model_name: str):
        """
        Export model data to files
        """
        try:
            output_dir = f"model_data/{model_name}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Export basic structure info
            structure_info = {
                'name': model_name,
                'matrices': [],
                'vectors': [],
                'scalars': []
            }
            
            for key, data in model_data.items():
                if key.startswith('__'):
                    continue
                    
                if hasattr(data, 'shape'):
                    if len(data.shape) == 1:
                        structure_info['vectors'].append({
                            'name': key,
                            'size': data.shape[0],
                            'dtype': str(data.dtype)
                        })
                    elif len(data.shape) == 2:
                        try:
                            sparsity = 1 - np.count_nonzero(data) / data.size if data.size > 0 else 0.0
                            structure_info['matrices'].append({
                                'name': key,
                                'shape': data.shape,
                                'sparsity': float(sparsity),
                                'dtype': str(data.dtype)
                            })
                        except:
                            structure_info['matrices'].append({
                                'name': key,
                                'shape': data.shape,
                                'sparsity': 0.0,
                                'dtype': str(data.dtype)
                            })
                    else:
                        structure_info['scalars'].append({
                            'name': key,
                            'shape': data.shape,
                            'dtype': str(data.dtype)
                        })
                else:
                    structure_info['scalars'].append({
                        'name': key,
                        'type': type(data).__name__,
                        'value': str(data)
                    })
            
            # Save structure info
            with open(f"{output_dir}/structure_info.json", 'w') as f:
                json.dump(structure_info, f, indent=2, default=str)
            
            # Try to export COBRA data if available
            try:
                import cobra
                # Find the actual model file path
                model_file = self._find_model_file(model_name)
                if model_file and os.path.exists(model_file):
                    model = cobra.io.load_matlab_model(model_file)
                else:
                    raise FileNotFoundError(f"Model file not found for {model_name}")
                
                # Export metabolites
                metabolites_data = []
                for met in model.metabolites:
                    metabolites_data.append({
                        'id': met.id,
                        'name': met.name,
                        'compartment': met.compartment,
                        'formula': met.formula,
                        'charge': met.charge,
                        'reaction_count': len(met.reactions)
                    })
                
                import pandas as pd
                metabolites_df = pd.DataFrame(metabolites_data)
                metabolites_df.to_csv(f"{output_dir}/metabolites.csv", index=False)
                
                # Export reactions
                reactions_data = []
                for rxn in model.reactions:
                    reactions_data.append({
                        'id': rxn.id,
                        'name': rxn.name,
                        'reversibility': rxn.reversibility,
                        'lower_bound': rxn.lower_bound,
                        'upper_bound': rxn.upper_bound,
                        'metabolite_count': len(rxn.metabolites),
                        'gene_reaction_rule': rxn.gene_reaction_rule
                    })
                
                reactions_df = pd.DataFrame(reactions_data)
                reactions_df.to_csv(f"{output_dir}/reactions.csv", index=False)
                
                # Export genes
                genes_data = []
                for gene in model.genes:
                    genes_data.append({
                        'id': gene.id,
                        'name': gene.name,
                        'functional': gene.functional,
                        'reaction_count': len(gene.reactions)
                    })
                
                genes_df = pd.DataFrame(genes_data)
                genes_df.to_csv(f"{output_dir}/genes.csv", index=False)
                
                # Generate visualizations
                self._generate_visualizations(output_dir, metabolites_df, reactions_df, genes_df)
                
                # Return the generated figures for Streamlit display
                return self.streamlit_figures
                
            except Exception as e:
                print(f"Warning: Could not export COBRA data: {e}")
                # Return empty list if COBRA export fails
                return []
                
        except Exception as e:
            print(f"Warning: Could not export model data: {e}")
            # Return empty list if export fails
            return []
    
    def _generate_visualizations(self, output_dir: str, metabolites_df, reactions_df, genes_df):
        """
        Generate visualizations from CSV data
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            import pandas as pd
            
            # Set style
            plt.style.use('default')
            sns.set_palette("husl")
            
            # Create visualizations directory
            viz_dir = os.path.join(output_dir, "visualizations")
            os.makedirs(viz_dir, exist_ok=True)
            
            # Store generated figures for Streamlit display
            self.streamlit_figures = []
            
            # Set matplotlib backend for Streamlit compatibility
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            
            # 1. Metabolites by compartment
            if not metabolites_df.empty and 'compartment' in metabolites_df.columns:
                fig1, ax1 = plt.subplots(figsize=(10, 6))
                compartment_counts = metabolites_df['compartment'].value_counts()
                ax1.pie(compartment_counts.values, labels=compartment_counts.index, autopct='%1.1f%%')
                ax1.set_title('Metabolites Distribution by Compartment')
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, 'metabolites_by_compartment.png'), dpi=300, bbox_inches='tight')
                self.streamlit_figures.append(('Metabolites by Compartment', fig1))
                # Don't close the figure for Streamlit display
            
            # 2. Metabolites connectivity distribution
            if not metabolites_df.empty and 'reaction_count' in metabolites_df.columns:
                fig2, ax2 = plt.subplots(figsize=(12, 6))
                ax2.hist(metabolites_df['reaction_count'], bins=30, alpha=0.7, edgecolor='black')
                ax2.set_xlabel('Number of Reactions')
                ax2.set_ylabel('Number of Metabolites')
                ax2.set_title('Metabolites Connectivity Distribution')
                ax2.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, 'metabolites_connectivity.png'), dpi=300, bbox_inches='tight')
                self.streamlit_figures.append(('Metabolites Connectivity', fig2))
                # Don't close the figure for Streamlit display
            
            # 3. Reactions by reversibility
            if not reactions_df.empty and 'reversibility' in reactions_df.columns:
                fig3, ax3 = plt.subplots(figsize=(8, 6))
                reversibility_counts = reactions_df['reversibility'].value_counts()
                if len(reversibility_counts) == 2:
                    colors = ['#ff9999', '#66b3ff']
                    labels = ['Irreversible', 'Reversible']
                    ax3.pie(reversibility_counts.values, labels=labels, 
                           autopct='%1.1f%%', colors=colors)
                else:
                    ax3.pie(reversibility_counts.values, labels=reversibility_counts.index, 
                           autopct='%1.1f%%')
                ax3.set_title('Reactions by Reversibility')
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, 'reactions_by_reversibility.png'), dpi=300, bbox_inches='tight')
                self.streamlit_figures.append(('Reactions by Reversibility', fig3))
                # Don't close the figure for Streamlit display
            
            # 4. Reactions by metabolite count
            if not reactions_df.empty and 'metabolite_count' in reactions_df.columns:
                fig4, ax4 = plt.subplots(figsize=(12, 6))
                ax4.hist(reactions_df['metabolite_count'], bins=30, alpha=0.7, edgecolor='black')
                ax4.set_xlabel('Number of Metabolites')
                ax4.set_ylabel('Number of Reactions')
                ax4.set_title('Reactions Complexity Distribution')
                ax4.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, 'reactions_complexity.png'), dpi=300, bbox_inches='tight')
                self.streamlit_figures.append(('Reactions Complexity', fig4))
                # Don't close the figure for Streamlit display
            
            # 5. Genes by functionality
            if not genes_df.empty and 'functional' in genes_df.columns:
                fig5, ax5 = plt.subplots(figsize=(8, 6))
                functional_counts = genes_df['functional'].value_counts()
                if len(functional_counts) == 2:
                    colors = ['#ffcc99', '#99ff99']
                    labels = ['Non-functional', 'Functional']
                    ax5.pie(functional_counts.values, labels=labels, 
                           autopct='%1.1f%%', colors=colors)
                else:
                    ax5.pie(functional_counts.values, labels=functional_counts.index, 
                           autopct='%1.1f%%')
                ax5.set_title('Genes by Functionality')
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, 'genes_by_functionality.png'), dpi=300, bbox_inches='tight')
                self.streamlit_figures.append(('Genes by Functionality', fig5))
                # Don't close the figure for Streamlit display
            
            # 6. Genes by reaction count
            if not genes_df.empty and 'reaction_count' in genes_df.columns:
                fig6, ax6 = plt.subplots(figsize=(12, 6))
                ax6.hist(genes_df['reaction_count'], bins=30, alpha=0.7, edgecolor='black')
                ax6.set_xlabel('Number of Reactions')
                ax6.set_ylabel('Number of Genes')
                ax6.set_title('Genes Activity Distribution')
                ax6.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, 'genes_activity.png'), dpi=300, bbox_inches='tight')
                self.streamlit_figures.append(('Genes Activity', fig6))
                # Don't close the figure for Streamlit display
            
            # 7. Top metabolites by connectivity
            if not metabolites_df.empty and 'reaction_count' in metabolites_df.columns:
                fig7, ax7 = plt.subplots(figsize=(12, 8))
                top_metabolites = metabolites_df.nlargest(15, 'reaction_count')
                ax7.barh(range(len(top_metabolites)), top_metabolites['reaction_count'])
                ax7.set_yticks(range(len(top_metabolites)))
                ax7.set_yticklabels(top_metabolites['id'])
                ax7.set_xlabel('Number of Reactions')
                ax7.set_title('Top 15 Metabolites by Connectivity')
                ax7.invert_yaxis()
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, 'top_metabolites.png'), dpi=300, bbox_inches='tight')
                self.streamlit_figures.append(('Top Metabolites', fig7))
                # Don't close the figure for Streamlit display
            
            # 8. Top reactions by metabolite count
            if not reactions_df.empty and 'metabolite_count' in reactions_df.columns:
                fig8, ax8 = plt.subplots(figsize=(12, 8))
                top_reactions = reactions_df.nlargest(15, 'metabolite_count')
                ax8.barh(range(len(top_reactions)), top_reactions['metabolite_count'])
                ax8.set_yticks(range(len(top_reactions)))
                ax8.set_yticklabels(top_reactions['id'])
                ax8.set_xlabel('Number of Metabolites')
                ax8.set_title('Top 15 Reactions by Complexity')
                ax8.invert_yaxis()
                plt.tight_layout()
                plt.savefig(os.path.join(viz_dir, 'top_reactions.png'), dpi=300, bbox_inches='tight')
                self.streamlit_figures.append(('Top Reactions', fig8))
                # Don't close the figure for Streamlit display
            
            # 9. Model summary statistics
            # Create subplots
            fig9, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # Subplot 1: Model components
            components = ['Metabolites', 'Reactions', 'Genes']
            counts = [len(metabolites_df), len(reactions_df), len(genes_df)]
            colors = ['#ff9999', '#66b3ff', '#99ff99']
            ax1.bar(components, counts, color=colors, alpha=0.7)
            ax1.set_title('Model Components')
            ax1.set_ylabel('Count')
            for i, v in enumerate(counts):
                ax1.text(i, v + max(counts)*0.01, str(v), ha='center', va='bottom')
            
            # Subplot 2: Compartments
            if not metabolites_df.empty and 'compartment' in metabolites_df.columns:
                compartment_counts = metabolites_df['compartment'].value_counts()
                ax2.pie(compartment_counts.values, labels=compartment_counts.index, autopct='%1.1f%%')
                ax2.set_title('Metabolites by Compartment')
            
            # Subplot 3: Reversibility
            if not reactions_df.empty and 'reversibility' in reactions_df.columns:
                reversibility_counts = reactions_df['reversibility'].value_counts()
                if len(reversibility_counts) == 2:
                    ax3.pie(reversibility_counts.values, labels=['Irreversible', 'Reversible'], 
                           autopct='%1.1f%%', colors=['#ffcc99', '#99ff99'])
                else:
                    ax3.pie(reversibility_counts.values, labels=reversibility_counts.index, 
                           autopct='%1.1f%%')
                ax3.set_title('Reactions by Reversibility')
            
            # Subplot 4: Gene functionality
            if not genes_df.empty and 'functional' in genes_df.columns:
                functional_counts = genes_df['functional'].value_counts()
                if len(functional_counts) == 2:
                    ax4.pie(functional_counts.values, labels=['Non-functional', 'Functional'], 
                           autopct='%1.1f%%', colors=['#ffcc99', '#99ff99'])
                else:
                    ax4.pie(functional_counts.values, labels=functional_counts.index, 
                           autopct='%1.1f%%')
                ax4.set_title('Genes by Functionality')
            
            plt.tight_layout()
            plt.savefig(os.path.join(viz_dir, 'model_summary.png'), dpi=300, bbox_inches='tight')
            self.streamlit_figures.append(('Model Summary', fig9))
            # Don't close the figure for Streamlit display
            
            # Generate HTML report
            try:
                self._generate_html_report(output_dir, viz_dir, metabolites_df, reactions_df, genes_df)
            except Exception as e:
                print(f"Warning: Could not generate HTML report: {e}")
            
            print(f"📊 Visualizations generated in: {viz_dir}")
            
        except Exception as e:
            print(f"Warning: Could not generate visualizations: {e}")
    
    def _generate_html_report(self, output_dir: str, viz_dir: str, metabolites_df, reactions_df, genes_df):
        """
        Generate HTML report with visualizations
        """
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Model Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; text-align: center; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #007bff; margin-top: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; }}
        .stat-label {{ font-size: 0.9em; opacity: 0.9; }}
        .visualization {{ margin: 20px 0; text-align: center; }}
        .visualization img {{ max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        .data-table {{ margin: 20px 0; overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #007bff; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .download-links {{ margin: 20px 0; }}
        .download-links a {{ display: inline-block; margin: 5px; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
        .download-links a:hover {{ background-color: #0056b3; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 Model Analysis Report</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(metabolites_df)}</div>
                <div class="stat-label">Metabolites</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(reactions_df)}</div>
                <div class="stat-label">Reactions</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(genes_df)}</div>
                <div class="stat-label">Genes</div>
            </div>
        </div>
        
        <h2>📊 Visualizations</h2>
        
        <div class="visualization">
            <h3>Model Summary</h3>
            <img src="visualizations/model_summary.png" alt="Model Summary">
        </div>
        
        <div class="visualization">
            <h3>Metabolites by Compartment</h3>
            <img src="visualizations/metabolites_by_compartment.png" alt="Metabolites by Compartment">
        </div>
        
        <div class="visualization">
            <h3>Metabolites Connectivity Distribution</h3>
            <img src="visualizations/metabolites_connectivity.png" alt="Metabolites Connectivity">
        </div>
        
        <div class="visualization">
            <h3>Reactions by Reversibility</h3>
            <img src="visualizations/reactions_by_reversibility.png" alt="Reactions by Reversibility">
        </div>
        
        <div class="visualization">
            <h3>Reactions Complexity Distribution</h3>
            <img src="visualizations/reactions_complexity.png" alt="Reactions Complexity">
        </div>
        
        <div class="visualization">
            <h3>Genes by Functionality</h3>
            <img src="visualizations/genes_by_functionality.png" alt="Genes by Functionality">
        </div>
        
        <div class="visualization">
            <h3>Genes Activity Distribution</h3>
            <img src="visualizations/genes_activity.png" alt="Genes Activity">
        </div>
        
        <div class="visualization">
            <h3>Top 15 Metabolites by Connectivity</h3>
            <img src="visualizations/top_metabolites.png" alt="Top Metabolites">
        </div>
        
        <div class="visualization">
            <h3>Top 15 Reactions by Complexity</h3>
            <img src="visualizations/top_reactions.png" alt="Top Reactions">
        </div>
        
        <h2>📁 Download Data</h2>
        <div class="download-links">
            <a href="metabolites.csv" download>Download Metabolites CSV</a>
            <a href="reactions.csv" download>Download Reactions CSV</a>
            <a href="genes.csv" download>Download Genes CSV</a>
            <a href="structure_info.json" download>Download Structure Info JSON</a>
        </div>
        
        <h2>📋 Data Preview</h2>
        
        <h3>Top 10 Metabolites</h3>
        <div class="data-table">
            {metabolites_df.head(10).to_html(classes='data-table', index=False) if not metabolites_df.empty else '<p>No metabolites data available</p>'}
        </div>
        
        <h3>Top 10 Reactions</h3>
        <div class="data-table">
            {reactions_df.head(10).to_html(classes='data-table', index=False) if not reactions_df.empty else '<p>No reactions data available</p>'}
        </div>
        
        <h3>Top 10 Genes</h3>
        <div class="data-table">
            {genes_df.head(10).to_html(classes='data-table', index=False) if not genes_df.empty else '<p>No genes data available</p>'}
        </div>
    </div>
</body>
</html>
            """
            
            with open(os.path.join(output_dir, 'analysis_report.html'), 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"📄 HTML report generated: {os.path.join(output_dir, 'analysis_report.html')}")
            
        except Exception as e:
            print(f"Warning: Could not generate HTML report: {e}")
    
    def _generate_cobra_visual_analysis(self, model_file: str, model_name: str) -> str:
        """
        Generate cobra visual analysis (fluxmap and network graphs)
        
        Args:
            model_file: Path to the .mat model file
            model_name: Name of the model
            
        Returns:
            str: Analysis result message
        """
        try:
            if not self.cobra_visual_agent:
                return "\n⚠️ CobraVisualAgent not available. Skipping fluxmap generation."
            
            print(f"🎨 Generating cobra visual analysis for {model_name}...")
            
            # Create output directory for cobra visual results
            cobra_output_dir = f"model_data/{model_name}/cobra_visual"
            os.makedirs(cobra_output_dir, exist_ok=True)
            
            # Configure cobra visual agent request
            request = {
                'model_path': model_file,
                'output_dir': cobra_output_dir,
                'visualization_types': ['network', 'fluxmap', 'analysis'],
                'analysis_level': 'comprehensive'
            }
            
            # Execute cobra visual analysis
            result = self.cobra_visual_agent.process_request(request)
            
            if result['success']:
                # Add cobra visual figures to streamlit figures
                cobra_figures = self._collect_cobra_visual_figures(cobra_output_dir, model_name)
                self.streamlit_figures.extend(cobra_figures)
                
                # Generate result message
                result_msg = f"\n🎨 Cobra Visual Analysis Results:\n"
                result_msg += "-" * 40 + "\n"
                result_msg += f"📁 Output directory: {cobra_output_dir}\n"
                
                # List generated files
                if os.path.exists(cobra_output_dir):
                    files = os.listdir(cobra_output_dir)
                    result_msg += f"📊 Generated files ({len(files)}):\n"
                    for file in sorted(files):
                        if file.endswith('.png'):
                            result_msg += f"  🖼️ {file}\n"
                        elif file.endswith('.html'):
                            result_msg += f"  📄 {file}\n"
                        elif file.endswith('.csv'):
                            result_msg += f"  📊 {file}\n"
                
                result_msg += f"\n✅ Cobra visual analysis completed successfully!"
                return result_msg
            else:
                return f"\n❌ Cobra visual analysis failed: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            return f"\n❌ Error in cobra visual analysis: {str(e)}"
    
    def _collect_cobra_visual_figures(self, cobra_output_dir: str, model_name: str) -> list:
        """
        Collect cobra visual figures for Streamlit display
        
        Args:
            cobra_output_dir: Directory containing cobra visual results
            model_name: Name of the model
            
        Returns:
            list: List of figure information for Streamlit
        """
        figures = []
        
        try:
            if not os.path.exists(cobra_output_dir):
                return figures
            
            # Define expected cobra visual files
            expected_files = [
                ('metabolic_network_graph.png', 'Complete metabolic network showing all reactions and their connections'),
                ('metabolic_fluxmap.png', 'Metabolic Fluxmap'),
                ('pathway_flux_heatmap.png', 'Pathway Flux Heatmap'),
                ('flux_distribution_plots.png', 'Flux Distribution Analysis')
            ]
            
            for filename, title in expected_files:
                file_path = os.path.join(cobra_output_dir, filename)
                if os.path.exists(file_path):
                    # Special handling for metabolic network graph to match Flux Distribution Analysis format
                    if filename == 'metabolic_network_graph.png':
                        figures.append({
                            'title': f"Cobra Visual - {title}",
                            'path': file_path,
                            'type': 'image',
                            'description': f'Cobra visual analysis: {title} for {model_name}'
                        })
                    else:
                        figures.append({
                            'title': f"Cobra Visual - {title}",
                            'path': file_path,
                            'type': 'image',
                            'description': f'Cobra visual analysis: {title} for {model_name}'
                        })
            

            
        except Exception as e:
            print(f"Warning: Error collecting cobra visual figures: {e}")
        
        return figures
    
    def _generate_ai_analysis(self, model_name: str, model_data: dict, cobra_result: str, structured_result: str) -> str:
        """
        Generate AI-powered analysis insights using LLM
        
        Args:
            model_name: Name of the model
            model_data: Model data dictionary
            cobra_result: COBRA analysis results
            structured_result: Structured model analysis results
            
        Returns:
            str: AI-generated analysis report
        """
        try:
            # Prepare analysis data for LLM
            analysis_data = f"""
Model Name: {model_name}

Basic Model Structure:
- Total data objects: {len([k for k in model_data.keys() if not k.startswith('__')])}
- Structured arrays: {len([k for k, v in model_data.items() if not k.startswith('__') and hasattr(v, 'dtype') and v.dtype.names])}
- Matrices: {len([k for k, v in model_data.items() if not k.startswith('__') and hasattr(v, 'shape') and len(v.shape) == 2])}
- Vectors: {len([k for k, v in model_data.items() if not k.startswith('__') and hasattr(v, 'shape') and len(v.shape) == 1])}

COBRA Analysis Results:
{cobra_result if cobra_result else "No COBRA analysis available"}

Structured Model Analysis:
{structured_result if structured_result else "No structured analysis available"}
"""

            # Create a prompt for LLM analysis
            analysis_prompt = f"""
You are a metabolic model analysis expert. Analyze the following results from a COBRA metabolic model analysis and provide comprehensive insights.

{analysis_data}

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
            
            print(f"🤖 Generating AI analysis for {model_name}...")
            analysis_report = llm_agent.chat(analysis_prompt)
            
            # Format the AI analysis
            formatted_analysis = f"📊 AI-Generated Analysis\n"
            formatted_analysis += "-" * 30 + "\n"
            formatted_analysis += analysis_report
            formatted_analysis += "\n\n"
            
            return formatted_analysis
            
        except Exception as e:
            print(f"Warning: Could not generate AI analysis: {e}")
            return ""
    
    def _generate_technical_details(self, model_name: str) -> str:
        """
        Generate technical details and usage instructions
        
        Args:
            model_name: Name of the model
            
        Returns:
            str: Technical details and usage instructions
        """
        try:
            technical_details = f"\n🔧 Technical Details\n"
            technical_details += "-" * 30 + "\n"
            
            # Check for generated files
            model_data_dir = f"model_data/{model_name}"
            if os.path.exists(model_data_dir):
                technical_details += "📁 Generated Files:\n"
                
                # Check regular analysis files
                regular_files = ['metabolites.csv', 'reactions.csv', 'genes.csv', 'structure_info.json', 'analysis_report.html']
                for file in regular_files:
                    file_path = os.path.join(model_data_dir, file)
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        technical_details += f"  • {file} ({file_size:,} bytes)\n"
                
                # Check visualizations directory
                viz_dir = os.path.join(model_data_dir, 'visualizations')
                if os.path.exists(viz_dir):
                    vis_files = [f for f in os.listdir(viz_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.svg', '.pdf'))]
                    if vis_files:
                        technical_details += f"  • visualizations/ ({len(vis_files)} files)\n"
                
                # Check cobra visual directory
                cobra_visual_dir = os.path.join(model_data_dir, 'cobra_visual')
                if os.path.exists(cobra_visual_dir):
                    cobra_files = [f for f in os.listdir(cobra_visual_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.svg', '.pdf', '.html', '.csv'))]
                    if cobra_files:
                        technical_details += f"  • cobra_visual/ ({len(cobra_files)} files)\n"
                
                technical_details += "\n"
            else:
                technical_details += "No generated files found.\n\n"
            
            # Add visualization information
            technical_details += "📈 Visualizations\n"
            technical_details += "-" * 30 + "\n"
            
            if hasattr(self, 'streamlit_figures') and self.streamlit_figures:
                technical_details += f"Generated {len(self.streamlit_figures)} visualization figures:\n"
                
                # Count different types
                regular_count = len([f for f in self.streamlit_figures if not (isinstance(f, dict) and f.get('title', f.get('name', '')).startswith('Cobra Visual -'))])
                cobra_count = len([f for f in self.streamlit_figures if isinstance(f, dict) and f.get('title', f.get('name', '')).startswith('Cobra Visual -')])
                
                technical_details += f"  • Basic analysis charts: {regular_count}\n"
                technical_details += f"  • Cobra visual charts: {cobra_count}\n"
            else:
                technical_details += "No visualization figures generated.\n"
            
            technical_details += "\n"
            
            # Add usage instructions
            technical_details += "💡 Usage Instructions\n"
            technical_details += "-" * 30 + "\n"
            technical_details += "• View generated files in the model_data directory\n"
            technical_details += "• Check the visualizations subdirectory for basic analysis charts\n"
            technical_details += "• Check the cobra_visual subdirectory for advanced fluxmap visualizations\n"
            technical_details += "• Use the CSV files for further data analysis\n"
            technical_details += "• The HTML reports provide comprehensive summaries\n"
            technical_details += "• The AI analysis provides biological insights and applications\n\n"
            
            return technical_details
            
        except Exception as e:
            print(f"Warning: Could not generate technical details: {e}")
            return ""
    
    def chat(self, prompt: str, memory=None) -> str:
        """
        Chat interface for model analysis
        """
        return self.run(prompt, memory) 