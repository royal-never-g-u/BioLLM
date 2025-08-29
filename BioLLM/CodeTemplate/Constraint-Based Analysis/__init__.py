"""
Constraint-Based Analysis Template Package

This package provides a comprehensive template for performing constraint-based 
metabolic analysis using COBRApy. The template includes configurable slots that 
agents can fill in to customize the analysis for different models and parameters.

Main Components:
- constraint_based_analysis_template.py: Main template with slots
- config_template.py: Configuration examples and usage instructions
- example_usage.py: Example usage demonstrations
- README.md: Comprehensive documentation

Usage:
    from BioLLM.CodeTemplate.Constraint_Based_Analysis import constraint_based_analysis_template
    # Configure slots and run analysis
"""

__version__ = "1.0.0"
__author__ = "BioLLM Team"
__description__ = "Constraint-Based Analysis Template with Configurable Slots"

# Import main template components
try:
    from . import constraint_based_analysis_template
    from . import config_template
    from . import example_usage
except ImportError:
    # If running as standalone, these imports may fail
    pass

# Template information
TEMPLATE_INFO = {
    "name": "Constraint-Based Analysis Template",
    "version": __version__,
    "description": "Comprehensive constraint-based metabolic analysis template with configurable slots",
    "main_file": "constraint_based_analysis_template.py",
    "config_file": "config_template.py",
    "example_file": "example_usage.py",
    "documentation": "README.md",
    "slots": {
        "model_configuration": [
            "model_file_path",
            "output_directory", 
            "model_format",
            "preprocess_model",
            "remove_blocked_reactions",
            "set_objective"
        ],
        "analysis_parameters": [
            "essentiality_threshold",
            "carbon_sources",
            "carbon_exchange_mapping",
            "environmental_conditions",
            "ph_conditions",
            "temperature_conditions",
            "central_reactions"
        ],
        "analysis_options": [
            "perform_basic_info",
            "perform_fba",
            "perform_growth_analysis",
            "perform_environmental_analysis",
            "perform_essentiality_analysis",
            "create_visualizations"
        ]
    },
    "capabilities": [
        "Model loading (SBML, JSON, MAT formats)",
        "Basic model information analysis",
        "Flux Balance Analysis (FBA)",
        "Growth capability analysis",
        "Environmental conditions testing",
        "Essential reactions analysis",
        "Results visualization and reporting"
    ],
    "dependencies": [
        "cobra",
        "pandas", 
        "numpy",
        "matplotlib",
        "seaborn"
    ]
}

def get_template_info():
    """
    Get information about the template and its capabilities.
    
    Returns:
        dict: Template information dictionary
    """
    return TEMPLATE_INFO

def list_available_slots():
    """
    List all available slots that can be configured.
    
    Returns:
        dict: Dictionary of slot categories and their slots
    """
    return TEMPLATE_INFO["slots"]

def get_example_configurations():
    """
    Get example configurations for different model types.
    
    Returns:
        dict: Example configurations
    """
    return {
        "ecoli_iml1515": {
            "description": "E. coli iML1515 comprehensive analysis",
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
        },
        "yeast": {
            "description": "Yeast model analysis",
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
                "ph_conditions": {"Acidic": 5.0, "Neutral": 0.0, "Basic": -5.0},
                "temperature_conditions": {"Low": 3.0, "Optimal": 6.0, "High": 12.0},
                "central_reactions": ["HEX1", "PFK", "FBA", "TPI", "TDH1", "PGK", "PGM", "ENO", "PYK"],
                "perform_basic_info": True,
                "perform_fba": True,
                "perform_growth_analysis": True,
                "perform_environmental_analysis": False,
                "perform_essentiality_analysis": True,
                "create_visualizations": True
            }
        },
        "minimal": {
            "description": "Minimal analysis with default model",
            "model_file_path": "",
            "output_directory": "",
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
    }

def print_template_summary():
    """
    Print a summary of the template capabilities and usage.
    """
    print("=" * 60)
    print("CONSTRAINT-BASED ANALYSIS TEMPLATE")
    print("=" * 60)
    print(f"Version: {__version__}")
    print(f"Description: {__description__}")
    print()
    
    print("CAPABILITIES:")
    for capability in TEMPLATE_INFO["capabilities"]:
        print(f"  • {capability}")
    print()
    
    print("AVAILABLE SLOTS:")
    for category, slots in TEMPLATE_INFO["slots"].items():
        print(f"  {category.replace('_', ' ').title()}:")
        for slot in slots:
            print(f"    • {slot}")
        print()
    
    print("DEPENDENCIES:")
    for dep in TEMPLATE_INFO["dependencies"]:
        print(f"  • {dep}")
    print()
    
    print("EXAMPLE CONFIGURATIONS:")
    examples = get_example_configurations()
    for name, config in examples.items():
        print(f"  • {name}: {config['description']}")
    print()
    
    print("USAGE:")
    print("  1. Configure slots in constraint_based_analysis_template.py")
    print("  2. Run: python constraint_based_analysis_template.py")
    print("  3. Check results in output directory")
    print()
    print("For detailed documentation, see README.md")

if __name__ == "__main__":
    print_template_summary()
