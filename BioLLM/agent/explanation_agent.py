#!/usr/bin/env python3
"""
Explanation Agent for Biological Metabolic Network Analysis

This agent provides detailed explanations about parameter settings, optimization goals,
and advantages of using specific metabolic models for particular analysis tasks.
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bio_task import get_current_task
from analysis_types import get_analysis_type_description


class ExplanationAgent:
    """
    Agent for explaining metabolic model analysis parameters and procedures
    """
    
    def __init__(self):
        """Initialize the ExplanationAgent"""
        self.base_prompt = """You are a computational biology expert with extensive knowledge of various biological metabolic network models and experimental procedures. When using a particular model for a specific task, what are the commonly used parameter settings, what is the optimization goal, and what are the advantages and characteristics of using this metabolic model for this task?"""
        
    def generate_explanation(self, model_name: str = None, task_type: int = None) -> Dict[str, Any]:
        """
        Generate explanation for a specific model and task type
        
        Args:
            model_name (str, optional): Name of the metabolic model. If None, reads from bio_task
            task_type (int, optional): Type of analysis task. If None, reads from bio_task
            
        Returns:
            Dict containing explanation result
        """
        try:
            # Get current task if parameters not provided
            if model_name is None or task_type is None:
                try:
                    current_task = get_current_task()
                    model_name = model_name or current_task.model_name
                    task_type = task_type or current_task.task_type
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Failed to read bio_task: {str(e)}',
                        'explanation': None
                    }
            
            # Validate parameters
            if not model_name:
                return {
                    'success': False,
                    'error': 'Model name is required',
                    'explanation': None
                }
            
            if task_type is None:
                return {
                    'success': False,
                    'error': 'Task type is required',
                    'explanation': None
                }
            
            # Get task type description
            try:
                task_description = get_analysis_type_description(task_type)
            except:
                task_description = f"Task Type {task_type}"
            
            # Create prompt with slots filled
            filled_prompt = self._create_filled_prompt(model_name, task_description)
            
            # Generate explanation using LLM
            explanation = self._generate_llm_response(filled_prompt)
            
            # Add experiment prompt
            full_explanation = self._add_experiment_prompt(explanation)
            
            return {
                'success': True,
                'model_name': model_name,
                'task_type': task_type,
                'task_description': task_description,
                'explanation': full_explanation,
                'prompt_used': filled_prompt
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': None
            }
    
    def _create_filled_prompt(self, model_name: str, task_description: str) -> str:
        """
        Create filled prompt by replacing slots with actual values
        
        Args:
            model_name (str): Name of the metabolic model
            task_description (str): Description of the analysis task
            
        Returns:
            str: Filled prompt
        """
        # Replace slots in the base prompt
        filled_prompt = self.base_prompt.replace(
            "a particular model for a specific task",
            f"the {model_name} model for {task_description}"
        )
        
        return filled_prompt
    
    def _generate_llm_response(self, prompt: str) -> str:
        """
        Generate LLM response for the given prompt
        
        Args:
            prompt (str): The prompt to send to LLM
            
        Returns:
            str: LLM response
        """
        # For now, we'll simulate LLM response
        # In a real implementation, this would call an actual LLM API
        
        # Simulate different responses based on model and task
        if "e_coli" in prompt.lower():
            if "flux balance" in prompt.lower():
                return self._generate_fba_explanation()
            elif "gene knockout" in prompt.lower():
                return self._generate_gene_knockout_explanation()
            else:
                return self._generate_general_explanation()
        else:
            return self._generate_general_explanation()
    
    def _generate_fba_explanation(self) -> str:
        """Generate explanation for Flux Balance Analysis"""
        return """**Flux Balance Analysis (FBA) for E. coli Models**

**Common Parameter Settings:**
- Objective function: Biomass reaction (e.g., BIOMASS_Ec_iML1515_core_75p37M)
- Solver: GLPK, CPLEX, or Gurobi
- Constraint bounds: Based on experimental measurements
- Medium composition: M9 minimal medium or rich medium (LB)

**Optimization Goal:**
- Maximize biomass production rate
- Identify optimal flux distribution
- Predict growth rates under different conditions
- Analyze metabolic network capabilities

**Advantages and Characteristics:**
- **Computational Efficiency**: Fast optimization using linear programming
- **Genome-scale Coverage**: Analyzes entire metabolic network simultaneously
- **Constraint-based**: Incorporates experimental constraints and bounds
- **Predictive Power**: Can predict growth rates and metabolite production
- **Robustness**: Handles large-scale networks efficiently
- **Experimental Validation**: Results can be validated through growth experiments

**Typical Workflow:**
1. Load metabolic model (e.g., iML1515, e_coli_core)
2. Set medium constraints and bounds
3. Define objective function (usually biomass)
4. Run FBA optimization
5. Analyze flux distribution and growth predictions"""
    
    def _generate_gene_knockout_explanation(self) -> str:
        """Generate explanation for Gene Knockout Analysis"""
        return """**Gene Knockout Analysis for E. coli Models**

**Common Parameter Settings:**
- Knockout method: Single gene deletions or combinatorial knockouts
- Objective function: Biomass production or specific metabolite production
- Growth threshold: 0.1-1% of wild-type growth rate
- Analysis scope: All genes or specific gene sets (e.g., metabolic genes only)

**Optimization Goal:**
- Identify essential genes for growth
- Find gene targets for metabolic engineering
- Optimize product synthesis pathways
- Understand gene essentiality under different conditions

**Advantages and Characteristics:**
- **Systematic Analysis**: Evaluates all genes systematically
- **Engineering Insights**: Identifies potential targets for genetic modification
- **Condition-specific**: Can analyze gene essentiality under different media
- **Product Optimization**: Helps design strains for metabolite production
- **Experimental Validation**: Results can guide CRISPR-Cas9 experiments
- **Network Understanding**: Reveals metabolic network structure and dependencies

**Typical Workflow:**
1. Load metabolic model
2. Set growth medium and constraints
3. Perform single gene knockout simulations
4. Identify essential and non-essential genes
5. Analyze impact on target metabolite production
6. Rank genes by their effect on objective function"""
    
    def _generate_general_explanation(self) -> str:
        """Generate general explanation for metabolic models"""
        return """**Metabolic Network Analysis**

**Common Parameter Settings:**
- Model format: SBML, JSON, or COBRA format
- Solver: GLPK, CPLEX, Gurobi, or other LP/MILP solvers
- Constraint handling: Upper and lower bounds on reactions
- Medium definition: Carbon sources, nitrogen sources, and other nutrients

**Optimization Goal:**
- Understand metabolic network behavior
- Predict cellular phenotypes
- Identify metabolic engineering targets
- Analyze network robustness and flexibility

**Advantages and Characteristics:**
- **Comprehensive Analysis**: Covers entire metabolic network
- **Constraint-based**: Incorporates biological and experimental constraints
- **Predictive Modeling**: Can predict outcomes before experiments
- **Scalable**: Works with models of varying complexity
- **Validatable**: Results can be experimentally verified
- **Flexible**: Can be adapted for different organisms and conditions

**Typical Workflow:**
1. Load and validate metabolic model
2. Set appropriate constraints and bounds
3. Define analysis objective
4. Run computational analysis
5. Interpret and validate results
6. Apply insights to experimental design"""
    
    def _add_experiment_prompt(self, explanation: str) -> str:
        """
        Add experiment prompt to the end of explanation
        
        Args:
            explanation (str): The main explanation text
            
        Returns:
            str: Explanation with experiment prompt added
        """
        experiment_prompt = "\n\n---\n\n**Do you want to experiment like this?**"
        return explanation + experiment_prompt


def generate_model_explanation(model_name: str = None, task_type: int = None) -> str:
    """
    Global function to generate model explanation
    
    Args:
        model_name (str, optional): Name of the metabolic model
        task_type (int, optional): Type of analysis task
        
    Returns:
        str: Generated explanation with experiment prompt
    """
    agent = ExplanationAgent()
    result = agent.generate_explanation(model_name, task_type)
    
    if result['success']:
        return result['explanation']
    else:
        return f"Error generating explanation: {result.get('error', 'Unknown error')}"


def get_explanation_agent() -> ExplanationAgent:
    """
    Get an instance of ExplanationAgent
    
    Returns:
        ExplanationAgent: Agent instance
    """
    return ExplanationAgent()


if __name__ == "__main__":
    # Test the explanation agent
    print("🧪 Testing Explanation Agent")
    print("=" * 50)
    
    agent = ExplanationAgent()
    
    # Test with e_coli_core and FBA
    print("\n📊 Testing with e_coli_core and FBA (task_type=1):")
    result1 = agent.generate_explanation("e_coli_core", 1)
    if result1['success']:
        print(f"✅ Success: {result1['explanation'][:200]}...")
    else:
        print(f"❌ Error: {result1['error']}")
    
    # Test with iMM904 and Gene Knockout
    print("\n📊 Testing with iMM904 and Gene Knockout (task_type=2):")
    result2 = agent.generate_explanation("iMM904", 2)
    if result2['success']:
        print(f"✅ Success: {result2['explanation'][:200]}...")
    else:
        print(f"❌ Error: {result2['error']}")
    
    # Test with bio_task data
    print("\n📊 Testing with bio_task data:")
    result3 = agent.generate_explanation()
    if result3['success']:
        print(f"✅ Success: {result3['explanation'][:200]}...")
    else:
        print(f"❌ Error: {result3['error']}")
    
    print("\n🎉 Explanation Agent test completed!")
