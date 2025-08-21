#!/usr/bin/env python3
"""
Next Step Agent for Biological Metabolic Network Analysis

This agent determines the next step based on the current bio_task configuration,
providing appropriate guidance for model selection or experiment planning.
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bio_task import get_current_task
from analysis_types import get_analysis_type_description, ANALYSIS_TYPES
from agent.explanation_agent import generate_model_explanation
from agent.rag_tool import RAGTool


class NextStepAgent:
    """
    Agent for determining the next step in metabolic analysis workflow
    """
    
    def __init__(self):
        """Initialize the NextStepAgent"""
        self.model_recommendation_prompt = """You are an expert in computational biology. What biological metabolic model do you recommend for a certain task?"""
        
        # Initialize RAG tool for knowledge base integration
        self.rag_tool = RAGTool()
        
        # Define available experiments for each task type
        self.available_experiments = {
            1: [  # Flux Balance Analysis (FBA)
                "Flux Balance Analysis (FBA)",
                "Prediction of optimal growth rates",
                "Analysis of metabolic flux distributions",
                "Optimization of biomass production"
            ],
            2: [  # Gene Knockout Analysis
                "Gene Knockout Analysis",
                "Prediction of single-gene knockout effects",
                "Double-gene knockout analysis",
                "Identification of essential genes"
            ],
            3: [  # Phenotype Prediction
                "Phenotype Prediction",
                "Growth prediction under different nutrient conditions",
                "Prediction of metabolite production yields",
                "Analysis of environmental adaptability"
            ],
            4: [  # Pathway Analysis
                "Pathway Analysis",
                "Assessment of metabolic pathway activity",
                "Identification of key reactions",
                "Analysis of metabolic bottlenecks"
            ],
            5: [  # Evolutionary Analysis
                "Evolutionary Analysis",
                "Simulation of adaptive evolution",
                "Trade-off analysis",
                "Pareto optimality analysis"
            ],
            6: [  # Constraint-Based Analysis
                "Constraint-Based Analysis",
                "Flux Variability Analysis (FVA)",
                "Assessment of reaction feasibility",
                "Analysis of metabolic network redundancy"
            ]
        }
    
    def if_next_step(self) -> Dict[str, Any]:
        """
        Determine the next step based on bio_task configuration
        
        Returns:
            Dict containing the next step information and action to take
        """
        try:
            # Read current bio_task
            current_task = get_current_task()
            
            # Check what information is available
            has_model_name = bool(current_task.model_name and current_task.model_name.strip())
            has_task_type = current_task.task_type is not None
            
            # Case 1: Neither model_name nor task_type exists
            if not has_model_name and not has_task_type:
                return {
                    'success': True,
                    'action': 'none',
                    'message': 'No model name or task type found in bio_task. Please set up your analysis configuration first.',
                    'model_name': None,
                    'task_type': None,
                    'task_description': None
                }
            
            # Case 2: Only model_name exists
            elif has_model_name and not has_task_type:
                return self._handle_model_only(current_task.model_name)
            
            # Case 3: Only task_type exists
            elif not has_model_name and has_task_type:
                return self._handle_task_only(current_task.task_type)
            
            # Case 4: Both model_name and task_type exist
            else:
                return self._handle_both_available(current_task.model_name, current_task.task_type)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'error',
                'message': f'Error reading bio_task: {str(e)}'
            }
    
    def _handle_model_only(self, model_name: str) -> Dict[str, Any]:
        """
        Handle case when only model_name exists
        
        Args:
            model_name (str): Name of the metabolic model
            
        Returns:
            Dict containing experiment options
        """
        # Create experiment options for all task types
        all_experiments = []
        for task_type, experiments in self.available_experiments.items():
            task_description = get_analysis_type_description(task_type)
            all_experiments.append(f"**{task_description}**")
            for experiment in experiments:
                all_experiments.append(f"• {experiment}")
            all_experiments.append("")  # Add empty line between task types
        
        experiment_list = "\n".join(all_experiments)
        
        message = f"""Would you like to conduct any of the following experiments with the {model_name} model?

{experiment_list}

Please specify which type of analysis you would like to perform."""
        
        return {
            'success': True,
            'action': 'model_only',
            'message': message,
            'model_name': model_name,
            'task_type': None,
            'task_description': None,
            'available_experiments': self.available_experiments
        }
    
    def _handle_task_only(self, task_type: int) -> Dict[str, Any]:
        """
        Handle case when only task_type exists
        
        Args:
            task_type (int): Type of analysis task
            
        Returns:
            Dict containing model recommendation with knowledge base integration
        """
        try:
            # Get task description
            task_description = get_analysis_type_description(task_type)
            
            # Create filled prompt
            filled_prompt = self.model_recommendation_prompt.replace(
                "a certain task",
                task_description
            )
            
            # Generate model recommendation using LLM with knowledge base integration
            model_recommendation = self._generate_model_recommendation_with_knowledge(filled_prompt, task_type)
            
            return {
                'success': True,
                'action': 'task_only',
                'message': model_recommendation,
                'model_name': None,
                'task_type': task_type,
                'task_description': task_description,
                'prompt_used': filled_prompt
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'error',
                'message': f'Error generating model recommendation: {str(e)}'
            }
    
    def _handle_both_available(self, model_name: str, task_type: int) -> Dict[str, Any]:
        """
        Handle case when both model_name and task_type exist
        
        Args:
            model_name (str): Name of the metabolic model
            task_type (int): Type of analysis task
            
        Returns:
            Dict containing explanation and next step information
        """
        try:
            # Call explanation agent to generate detailed explanation
            explanation = generate_model_explanation(model_name, task_type)
            
            # Create enhanced message with explanation
            task_description = get_analysis_type_description(task_type)
            
            message = f"""✅ **Configuration Complete!**

**Model**: {model_name}
**Task Type**: {task_description}

---

{explanation}

---

**Next Steps:**
- You can now proceed with the analysis using the {model_name} model
- The system is ready to execute {task_description}
- Use the appropriate analysis commands to start your experiment"""
            
            return {
                'success': True,
                'action': 'both_available',
                'message': message,
                'model_name': model_name,
                'task_type': task_type,
                'task_description': task_description,
                'explanation': explanation
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'action': 'error',
                'message': f'Error generating explanation: {str(e)}'
            }
    
    def _generate_model_recommendation(self, prompt: str, task_type: int) -> str:
        """
        Generate model recommendation using LLM
        
        Args:
            prompt (str): The filled prompt
            task_type (int): Type of analysis task
            
        Returns:
            str: Model recommendation response
        """
        # For now, we'll simulate LLM response based on task type
        # In a real implementation, this would call an actual LLM API
        
        task_description = get_analysis_type_description(task_type)
        
        if task_type == 1:  # FBA
            return f"""**Model Recommendation for {task_description}**

Based on your request for {task_description}, I recommend the following metabolic models:

**Primary Recommendations:**
1. **e_coli_core** - A well-curated core model of E. coli metabolism, perfect for FBA analysis
2. **iML1515** - A comprehensive genome-scale model of E. coli K-12 MG1655
3. **iMM904** - A detailed model of S. cerevisiae (yeast) metabolism

**Why these models are suitable:**
- **e_coli_core**: Small, fast, and well-validated for FBA studies
- **iML1515**: Comprehensive coverage of E. coli metabolism with 1,515 genes
- **iMM904**: Excellent for comparative studies and eukaryotic metabolism

**Recommended starting point:** e_coli_core for quick analysis, iML1515 for comprehensive studies."""
        
        elif task_type == 2:  # Gene Knockout
            return f"""**Model Recommendation for {task_description}**

For {task_description}, I recommend these metabolic models:

**Primary Recommendations:**
1. **iML1515** - Comprehensive E. coli model with 1,515 genes, ideal for systematic knockout analysis
2. **e_coli_core** - Core model for essential gene identification
3. **iMM904** - Yeast model for eukaryotic gene knockout studies

**Why these models are suitable:**
- **iML1515**: Large gene set allows comprehensive knockout screening
- **e_coli_core**: Fast computation for essential gene identification
- **iMM904**: Eukaryotic perspective and well-annotated gene-reaction relationships

**Recommended starting point:** iML1515 for comprehensive gene knockout analysis."""
        
        elif task_type == 3:  # Phenotype Prediction
            return f"""**Model Recommendation for {task_description}**

For {task_description}, I recommend these metabolic models:

**Primary Recommendations:**
1. **iML1515** - Comprehensive E. coli model with detailed growth predictions
2. **iMM904** - Yeast model for eukaryotic phenotype prediction
3. **e_coli_core** - Core model for basic phenotype analysis

**Why these models are suitable:**
- **iML1515**: Detailed biomass composition and growth predictions
- **iMM904**: Eukaryotic metabolism and stress response modeling
- **e_coli_core**: Fast phenotype prediction under various conditions

**Recommended starting point:** iML1515 for detailed phenotype prediction."""
        
        elif task_type == 4:  # Pathway Analysis
            return f"""**Model Recommendation for {task_description}**

For {task_description}, I recommend these metabolic models:

**Primary Recommendations:**
1. **iML1515** - Comprehensive pathway coverage in E. coli
2. **iMM904** - Detailed yeast metabolic pathways
3. **e_coli_core** - Core pathways for fundamental analysis

**Why these models are suitable:**
- **iML1515**: Complete pathway representation with detailed annotations
- **iMM904**: Eukaryotic pathway complexity and regulation
- **e_coli_core**: Essential pathways for bottleneck analysis

**Recommended starting point:** iML1515 for comprehensive pathway analysis."""
        
        elif task_type == 5:  # Evolutionary Analysis
            return f"""**Model Recommendation for {task_description}**

For {task_description}, I recommend these metabolic models:

**Primary Recommendations:**
1. **iML1515** - Large-scale model for evolutionary trade-off analysis
2. **iMM904** - Eukaryotic model for evolutionary adaptation studies
3. **e_coli_core** - Core model for basic evolutionary principles

**Why these models are suitable:**
- **iML1515**: Comprehensive gene set for evolutionary simulation
- **iMM904**: Eukaryotic complexity and adaptation mechanisms
- **e_coli_core**: Fast computation for evolutionary optimization

**Recommended starting point:** iML1515 for comprehensive evolutionary analysis."""
        
        elif task_type == 6:  # Constraint-Based Analysis
            return f"""**Model Recommendation for {task_description}**

For {task_description}, I recommend these metabolic models:

**Primary Recommendations:**
1. **iML1515** - Comprehensive constraint-based analysis capabilities
2. **e_coli_core** - Core model for FVA and feasibility analysis
3. **iMM904** - Eukaryotic model for complex constraint analysis

**Why these models are suitable:**
- **iML1515**: Large reaction set for comprehensive FVA
- **e_coli_core**: Fast computation for constraint analysis
- **iMM904**: Complex constraints in eukaryotic metabolism

**Recommended starting point:** iML1515 for comprehensive constraint-based analysis."""
        
        else:
            return f"""**Model Recommendation for {task_description}**

For {task_description}, I recommend starting with:

**General Recommendations:**
1. **e_coli_core** - Well-curated core model for general analysis
2. **iML1515** - Comprehensive genome-scale model
3. **iMM904** - Eukaryotic model for comparative studies

**Choose based on your specific needs:**
- **e_coli_core**: For quick analysis and learning
- **iML1515**: For comprehensive studies
- **iMM904**: For eukaryotic perspective"""
    
    def _generate_model_recommendation_with_knowledge(self, prompt: str, task_type: int) -> str:
        """
        Generate model recommendation using LLM with knowledge base integration
        
        Args:
            prompt (str): The filled prompt
            task_type (int): Type of analysis task
            
        Returns:
            str: Enhanced model recommendation response with knowledge base content
        """
        try:
            # Get task description for search
            task_description = get_analysis_type_description(task_type)
            
            # Search knowledge base for relevant information
            knowledge_results = self._search_knowledge_base(task_description)
            
            # Combine prompt with knowledge base content
            enhanced_prompt = self._create_enhanced_prompt(prompt, knowledge_results)
            
            # Generate enhanced recommendation
            enhanced_recommendation = self._generate_enhanced_recommendation(enhanced_prompt, task_type, knowledge_results)
            
            return enhanced_recommendation
            
        except Exception as e:
            # Fallback to basic recommendation if knowledge base integration fails
            print(f"Warning: Knowledge base integration failed: {e}")
            return self._generate_model_recommendation(prompt, task_type)
    
    def _search_knowledge_base(self, query: str) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant information
        
        Args:
            query (str): Search query
            
        Returns:
            List of relevant knowledge base results
        """
        try:
            # Use RAG tool to search knowledge base
            search_results = self.rag_tool.search(query, top_k=5)
            return search_results
        except Exception as e:
            print(f"Warning: Knowledge base search failed: {e}")
            return []
    
    def _create_enhanced_prompt(self, original_prompt: str, knowledge_results: List[Dict[str, Any]]) -> str:
        """
        Create enhanced prompt with knowledge base content
        
        Args:
            original_prompt (str): Original prompt
            knowledge_results (List[Dict]): Knowledge base search results
            
        Returns:
            str: Enhanced prompt with knowledge base content
        """
        if not knowledge_results:
            return original_prompt
        
        # Extract relevant content from knowledge base results
        knowledge_content = []
        for result in knowledge_results:
            if 'content' in result:
                knowledge_content.append(result['content'])
            elif 'text' in result:
                knowledge_content.append(result['text'])
        
        if not knowledge_content:
            return original_prompt
        
        # Create enhanced prompt
        enhanced_prompt = f"""You are an expert in computational biology with access to the following knowledge base information:

**Knowledge Base Content:**
{chr(10).join(f"- {content[:200]}..." for content in knowledge_content[:3])}

**User Question:**
{original_prompt}

Please provide a comprehensive model recommendation that incorporates both your expertise and the relevant knowledge base information. Focus on practical recommendations that align with the available knowledge."""
        
        return enhanced_prompt
    
    def _generate_enhanced_recommendation(self, enhanced_prompt: str, task_type: int, knowledge_results: List[Dict[str, Any]]) -> str:
        """
        Generate enhanced model recommendation using LLM
        
        Args:
            enhanced_prompt (str): Enhanced prompt with knowledge base content
            task_type (int): Type of analysis task
            knowledge_results (List[Dict]): Knowledge base search results
            
        Returns:
            str: Enhanced model recommendation
        """
        # For now, we'll enhance the basic recommendation with knowledge base content
        # In a real implementation, this would call an actual LLM API with the enhanced prompt
        
        task_description = get_analysis_type_description(task_type)
        
        # Start with basic recommendation
        basic_recommendation = self._generate_model_recommendation(enhanced_prompt, task_type)
        
        # Add knowledge base integration section
        if knowledge_results:
            knowledge_section = self._create_knowledge_section(knowledge_results)
            enhanced_recommendation = f"""{basic_recommendation}

---

**📚 Knowledge Base Integration:**

{knowledge_section}

---

**💡 Enhanced Recommendation:**
This recommendation has been enhanced with relevant information from our knowledge base to provide more accurate and up-to-date model suggestions."""
        else:
            enhanced_recommendation = basic_recommendation
        
        return enhanced_recommendation
    
    def _create_knowledge_section(self, knowledge_results: List[Dict[str, Any]]) -> str:
        """
        Create knowledge base section for the recommendation
        
        Args:
            knowledge_results (List[Dict]): Knowledge base search results
            
        Returns:
            str: Formatted knowledge base section
        """
        if not knowledge_results:
            return "No relevant knowledge base information found."
        
        knowledge_section = "**Relevant Knowledge Base Information:**\n\n"
        
        for i, result in enumerate(knowledge_results[:3], 1):
            content = result.get('content', result.get('text', 'No content available'))
            # Truncate content for display
            display_content = content[:300] + "..." if len(content) > 300 else content
            
            knowledge_section += f"{i}. **Source**: {result.get('source', 'Unknown')}\n"
            knowledge_section += f"   **Content**: {display_content}\n\n"
        
        return knowledge_section
    
    def get_available_experiments_for_task(self, task_type: int) -> List[str]:
        """
        Get available experiments for a specific task type
        
        Args:
            task_type (int): Type of analysis task
            
        Returns:
            List of available experiments
        """
        return self.available_experiments.get(task_type, [])
    
    def get_all_available_experiments(self) -> Dict[int, List[str]]:
        """
        Get all available experiments for all task types
        
        Returns:
            Dict mapping task types to their available experiments
        """
        return self.available_experiments.copy()


def if_next_step() -> Dict[str, Any]:
    """
    Global function to determine the next step
    
    Returns:
        Dict containing the next step information
    """
    agent = NextStepAgent()
    return agent.if_next_step()


def get_next_step_agent() -> NextStepAgent:
    """
    Get an instance of NextStepAgent
    
    Returns:
        NextStepAgent: Agent instance
    """
    return NextStepAgent()


if __name__ == "__main__":
    # Test the next step agent
    print("🧪 Testing Next Step Agent")
    print("=" * 50)
    
    agent = NextStepAgent()
    
    # Test with different bio_task configurations
    print("\n📊 Testing if_next_step method:")
    result = agent.if_next_step()
    
    print(f"Success: {result['success']}")
    print(f"Action: {result['action']}")
    print(f"Message: {result['message']}")
    
    if result['success']:
        print(f"Model Name: {result.get('model_name', 'None')}")
        print(f"Task Type: {result.get('task_type', 'None')}")
        print(f"Task Description: {result.get('task_description', 'None')}")
    
    print("\n🎉 Next Step Agent test completed!")
