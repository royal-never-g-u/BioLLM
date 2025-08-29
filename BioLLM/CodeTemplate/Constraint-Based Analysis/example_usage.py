#!/usr/bin/env python3
"""
Example Usage of Constraint-Based Analysis Template
This file demonstrates how to use the template with different configurations.
"""

import os
import shutil
from pathlib import Path

def create_configured_template(config_name, config_params):
    """
    Create a configured template file from the base template.
    
    Args:
        config_name (str): Name for the configuration
        config_params (dict): Configuration parameters
    """
    # Read the base template
    template_path = "constraint_based_analysis_template.py"
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Replace slots with configuration values
    configured_content = template_content
    
    # Replace model file path
    model_path = config_params.get("model_file_path", "")
    configured_content = configured_content.replace('"{{model_file_path}}"', f'"{model_path}"')
    
    # Replace output directory
    output_dir = config_params.get("output_directory", "")
    configured_content = configured_content.replace('"{{output_directory}}"', f'"{output_dir}"')
    
    # Replace analysis parameters
    analysis_params = config_params.get("analysis_parameters", {})
    
    # Essentiality threshold
    threshold = analysis_params.get("essentiality_threshold", 0.01)
    configured_content = configured_content.replace('{{essentiality_threshold}}', str(threshold))
    
    # Carbon sources
    carbon_sources = analysis_params.get("carbon_sources", ["glucose"])
    configured_content = configured_content.replace('{{carbon_sources}}', str(carbon_sources))
    
    # Carbon exchange mapping
    carbon_mapping = analysis_params.get("carbon_exchange_mapping", {"glucose": "EX_glc__D_e"})
    configured_content = configured_content.replace('{{carbon_exchange_mapping}}', str(carbon_mapping))
    
    # Environmental conditions
    env_conditions = analysis_params.get("environmental_conditions", ["pH", "temperature"])
    configured_content = configured_content.replace('{{environmental_conditions}}', str(env_conditions))
    
    # pH conditions
    ph_conditions = analysis_params.get("ph_conditions", {"Neutral": 0.0})
    configured_content = configured_content.replace('{{ph_conditions}}', str(ph_conditions))
    
    # Temperature conditions
    temp_conditions = analysis_params.get("temperature_conditions", {"Optimal": 8.39})
    configured_content = configured_content.replace('{{temperature_conditions}}', str(temp_conditions))
    
    # Central reactions
    central_reactions = analysis_params.get("central_reactions", ["PGI", "PFK", "FBA"])
    configured_content = configured_content.replace('{{central_reactions}}', str(central_reactions))
    
    # Analysis options
    for option in ["perform_basic_info", "perform_fba", "perform_growth_analysis", 
                   "perform_environmental_analysis", "perform_essentiality_analysis", "create_visualizations"]:
        value = analysis_params.get(option, True)
        configured_content = configured_content.replace(f'{{{{{option}}}}}', str(value))
    
    # Replace model loading options
    model_options = config_params.get("model_loading_options", {})
    
    model_format = model_options.get("model_format", "auto")
    configured_content = configured_content.replace('{{model_format}}', f'"{model_format}"')
    
    preprocess = model_options.get("preprocess_model", False)
    configured_content = configured_content.replace('{{preprocess_model}}', str(preprocess))
    
    remove_blocked = model_options.get("remove_blocked_reactions", False)
    configured_content = configured_content.replace('{{remove_blocked_reactions}}', str(remove_blocked))
    
    objective = model_options.get("set_objective", None)
    if objective:
        configured_content = configured_content.replace('{{set_objective}}', f'"{objective}"')
    else:
        configured_content = configured_content.replace('{{set_objective}}', 'None')
    
    # Write configured template
    output_filename = f"configured_{config_name}_analysis.py"
    with open(output_filename, 'w') as f:
        f.write(configured_content)
    
    print(f"✓ Created configured template: {output_filename}")
    return output_filename

def run_example_analyses():
    """
    Run example analyses with different configurations.
    """
    print("CONSTRAINT-BASED ANALYSIS TEMPLATE - EXAMPLE USAGE")
    print("=" * 60)
    
    # Example 1: E. coli iML1515 analysis
    print("\n1. Creating E. coli iML1515 analysis configuration...")
    ecoli_config = {
        "model_file_path": "models/iML1515.xml",
        "output_directory": "results/ecoli_iml1515_analysis",
        "model_loading_options": {
            "model_format": "sbml",
            "preprocess_model": True,
            "remove_blocked_reactions": False,
            "set_objective": "BIOMASS_Ec_iML1515_core_75p37M"
        },
        "analysis_parameters": {
            "essentiality_threshold": 0.01,
            "carbon_sources": ["glucose", "fructose", "acetate", "succinate"],
            "carbon_exchange_mapping": {
                "glucose": "EX_glc__D_e",
                "fructose": "EX_fru_e",
                "acetate": "EX_ac_e",
                "succinate": "EX_succ_e"
            },
            "environmental_conditions": ["pH", "temperature", "osmotic"],
            "ph_conditions": {
                "Acidic": 10.0,
                "Neutral": 0.0,
                "Basic": -10.0
            },
            "temperature_conditions": {
                "Low": 5.0,
                "Optimal": 8.39,
                "High": 15.0
            },
            "central_reactions": [
                "PGI", "PFK", "FBA", "TPI", "GAPD", "PGK", "PGM", "ENO", "PYK",
                "CS", "ACONT", "ICDHyr", "AKGDH", "SUCOAS", "SUCDi", "FUM", "MDH"
            ],
            "perform_basic_info": True,
            "perform_fba": True,
            "perform_growth_analysis": True,
            "perform_environmental_analysis": True,
            "perform_essentiality_analysis": True,
            "create_visualizations": True
        }
    }
    
    ecoli_file = create_configured_template("ecoli_iml1515", ecoli_config)
    
    # Example 2: Yeast analysis
    print("\n2. Creating yeast analysis configuration...")
    yeast_config = {
        "model_file_path": "models/yeast_model.xml",
        "output_directory": "results/yeast_analysis",
        "model_loading_options": {
            "model_format": "sbml",
            "preprocess_model": True,
            "remove_blocked_reactions": True,
            "set_objective": "BIOMASS_SC5_notrace"
        },
        "analysis_parameters": {
            "essentiality_threshold": 0.05,
            "carbon_sources": ["glucose", "ethanol", "glycerol"],
            "carbon_exchange_mapping": {
                "glucose": "EX_glc_e",
                "ethanol": "EX_etoh_e",
                "glycerol": "EX_glyc_e"
            },
            "environmental_conditions": ["pH", "temperature"],
            "ph_conditions": {
                "Acidic": 5.0,
                "Neutral": 0.0,
                "Basic": -5.0
            },
            "temperature_conditions": {
                "Low": 3.0,
                "Optimal": 6.0,
                "High": 12.0
            },
            "central_reactions": [
                "HEX1", "PFK", "FBA", "TPI", "TDH1", "PGK", "PGM", "ENO", "PYK"
            ],
            "perform_basic_info": True,
            "perform_fba": True,
            "perform_growth_analysis": True,
            "perform_environmental_analysis": False,
            "perform_essentiality_analysis": True,
            "create_visualizations": True
        }
    }
    
    yeast_file = create_configured_template("yeast", yeast_config)
    
    # Example 3: Minimal analysis (uses default model)
    print("\n3. Creating minimal analysis configuration...")
    minimal_config = {
        "model_file_path": "",  # Will use default model
        "output_directory": "",  # Auto-generated
        "model_loading_options": {
            "model_format": "auto",
            "preprocess_model": False,
            "remove_blocked_reactions": False,
            "set_objective": None
        },
        "analysis_parameters": {
            "essentiality_threshold": 0.01,
            "carbon_sources": ["glucose"],
            "carbon_exchange_mapping": {
                "glucose": "EX_glc__D_e"
            },
            "environmental_conditions": [],
            "ph_conditions": {
                "Neutral": 0.0
            },
            "temperature_conditions": {
                "Optimal": 8.39
            },
            "central_reactions": ["PGI", "PFK", "FBA"],
            "perform_basic_info": True,
            "perform_fba": True,
            "perform_growth_analysis": False,
            "perform_environmental_analysis": False,
            "perform_essentiality_analysis": False,
            "create_visualizations": False
        }
    }
    
    minimal_file = create_configured_template("minimal", minimal_config)
    
    print("\n" + "=" * 60)
    print("CONFIGURED TEMPLATES CREATED:")
    print(f"1. {ecoli_file} - E. coli iML1515 comprehensive analysis")
    print(f"2. {yeast_file} - Yeast model analysis")
    print(f"3. {minimal_file} - Minimal analysis with default model")
    
    print("\nTO RUN THE ANALYSES:")
    print("1. Ensure you have the required model files in the 'models/' directory")
    print("2. Install dependencies: pip install cobra pandas numpy matplotlib seaborn")
    print("3. Run any of the configured templates:")
    print(f"   python {ecoli_file}")
    print(f"   python {yeast_file}")
    print(f"   python {minimal_file}")
    
    print("\nNOTE: The minimal analysis will work with the default E. coli core model")
    print("if no model file is specified or if the specified model cannot be loaded.")

def create_agent_usage_example():
    """
    Create an example showing how agents can programmatically use the template.
    """
    print("\n" + "=" * 60)
    print("AGENT USAGE EXAMPLE")
    print("=" * 60)
    
    agent_example = '''
# Example: How an agent can programmatically configure and run the analysis

import subprocess
import json

def run_agent_analysis(model_path, analysis_type="comprehensive"):
    """
    Agent function to run constraint-based analysis.
    
    Args:
        model_path (str): Path to metabolic model file
        analysis_type (str): Type of analysis ("comprehensive", "minimal", "custom")
    """
    
    # Define configurations based on analysis type
    if analysis_type == "comprehensive":
        config = {
            "model_file_path": model_path,
            "output_directory": f"results/{analysis_type}_analysis",
            "model_loading_options": {
                "model_format": "auto",
                "preprocess_model": True,
                "remove_blocked_reactions": False,
                "set_objective": None
            },
            "analysis_parameters": {
                "essentiality_threshold": 0.01,
                "carbon_sources": ["glucose", "fructose", "acetate"],
                "carbon_exchange_mapping": {
                    "glucose": "EX_glc__D_e",
                    "fructose": "EX_fru_e",
                    "acetate": "EX_ac_e"
                },
                "environmental_conditions": ["pH", "temperature"],
                "ph_conditions": {"Acidic": 10.0, "Neutral": 0.0, "Basic": -10.0},
                "temperature_conditions": {"Low": 5.0, "Optimal": 8.39, "High": 15.0},
                "central_reactions": ["PGI", "PFK", "FBA", "TPI", "GAPD", "PGK", "PGM", "ENO", "PYK"],
                "perform_basic_info": True,
                "perform_fba": True,
                "perform_growth_analysis": True,
                "perform_environmental_analysis": True,
                "perform_essentiality_analysis": True,
                "create_visualizations": True
            }
        }
    elif analysis_type == "minimal":
        config = {
            "model_file_path": model_path,
            "output_directory": f"results/{analysis_type}_analysis",
            "model_loading_options": {
                "model_format": "auto",
                "preprocess_model": False,
                "remove_blocked_reactions": False,
                "set_objective": None
            },
            "analysis_parameters": {
                "essentiality_threshold": 0.01,
                "carbon_sources": ["glucose"],
                "carbon_exchange_mapping": {"glucose": "EX_glc__D_e"},
                "environmental_conditions": [],
                "ph_conditions": {"Neutral": 0.0},
                "temperature_conditions": {"Optimal": 8.39},
                "central_reactions": ["PGI", "PFK", "FBA"],
                "perform_basic_info": True,
                "perform_fba": True,
                "perform_growth_analysis": False,
                "perform_environmental_analysis": False,
                "perform_essentiality_analysis": False,
                "create_visualizations": False
            }
        }
    
    # Create configured template
    template_file = create_configured_template(f"agent_{analysis_type}", config)
    
    # Run the analysis
    try:
        result = subprocess.run(["python", template_file], 
                              capture_output=True, text=True, check=True)
        print(f"Analysis completed successfully!")
        print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Analysis failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

# Example usage:
# run_agent_analysis("models/my_model.xml", "comprehensive")
# run_agent_analysis("models/another_model.xml", "minimal")
'''
    
    with open("agent_usage_example.py", 'w') as f:
        f.write(agent_example)
    
    print("✓ Created agent_usage_example.py")
    print("This file shows how agents can programmatically configure and run analyses.")

if __name__ == "__main__":
    run_example_analyses()
    create_agent_usage_example()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("You now have:")
    print("1. Three configured template files ready to run")
    print("2. An agent usage example showing programmatic configuration")
    print("3. All necessary documentation and examples")
    print("\nNext steps:")
    print("1. Install dependencies: pip install cobra pandas numpy matplotlib seaborn")
    print("2. Run any of the configured templates")
    print("3. Check the results in the output directories")
