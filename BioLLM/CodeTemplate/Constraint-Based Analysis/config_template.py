#!/usr/bin/env python3
"""
Configuration Template for Constraint-Based Analysis
This file shows how to configure the slots in the main template.

Copy this file and modify the values according to your needs.
"""

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Path to your metabolic model file
MODEL_FILE_PATH = "path/to/your/model.xml"  # SBML, JSON, or MAT format

# Output directory for results
OUTPUT_DIRECTORY = "results/constraint_analysis"  # Leave empty for auto-generated timestamped directory

# Model loading options
MODEL_LOADING_OPTIONS = {
    "model_format": "sbml",  # "sbml", "json", "mat", or "auto"
    "preprocess_model": True,  # Apply preprocessing
    "remove_blocked_reactions": False,  # Remove blocked reactions
    "set_objective": "BIOMASS_Ec_iML1515_core_75p37M"  # Set specific objective reaction
}

# =============================================================================
# ANALYSIS PARAMETERS
# =============================================================================

ANALYSIS_PARAMETERS = {
    # Growth rate threshold for essentiality analysis (fraction of wild-type)
    "essentiality_threshold": 0.01,  # 1% of wild-type growth
    
    # Carbon sources to test for growth capability
    "carbon_sources": [
        "glucose", "fructose", "acetate", "succinate", 
        "lactate", "glycerol", "pyruvate"
    ],
    
    # Carbon source exchange reaction mapping
    "carbon_exchange_mapping": {
        "glucose": "EX_glc__D_e",
        "fructose": "EX_fru_e",
        "acetate": "EX_ac_e",
        "succinate": "EX_succ_e",
        "lactate": "EX_lac__L_e",
        "glycerol": "EX_glyc_e",
        "pyruvate": "EX_pyr_e"
    },
    
    # Environmental conditions to test
    "environmental_conditions": ["pH", "temperature", "osmotic"],
    
    # pH conditions to test
    "ph_conditions": {
        "Acidic (pH 5)": 10.0,    # Higher proton availability
        "Neutral (pH 7)": 0.0,    # Balanced
        "Basic (pH 9)": -10.0     # Lower proton availability
    },
    
    # Temperature conditions to test
    "temperature_conditions": {
        "Low (20°C)": 5.0,        # Lower maintenance
        "Optimal (37°C)": 8.39,   # Normal maintenance
        "High (45°C)": 15.0       # Higher maintenance
    },
    
    # Central metabolism reactions to test for essentiality
    "central_reactions": [
        "PGI",     # Glucose-6-phosphate isomerase
        "PFK",     # Phosphofructokinase  
        "FBA",     # Fructose-bisphosphate aldolase
        "TPI",     # Triose phosphate isomerase
        "GAPD",    # Glyceraldehyde-3-phosphate dehydrogenase
        "PGK",     # Phosphoglycerate kinase
        "PGM",     # Phosphoglycerate mutase
        "ENO",     # Enolase
        "PYK",     # Pyruvate kinase
        "CS",      # Citrate synthase
        "ACONT",   # Aconitate hydratase
        "ICDHyr",  # Isocitrate dehydrogenase
        "AKGDH",   # α-ketoglutarate dehydrogenase
        "SUCOAS",  # Succinate-CoA synthetase
        "SUCDi",   # Succinate dehydrogenase
        "FUM",     # Fumarase
        "MDH"      # Malate dehydrogenase
    ],
    
    # Analysis options (which analyses to perform)
    "perform_basic_info": True,           # Basic model information
    "perform_fba": True,                  # Flux Balance Analysis
    "perform_growth_analysis": True,      # Growth capabilities
    "perform_environmental_analysis": True, # Environmental conditions
    "perform_essentiality_analysis": True, # Essential reactions
    "create_visualizations": True         # Create plots
}

# =============================================================================
# EXAMPLE CONFIGURATIONS FOR DIFFERENT MODELS
# =============================================================================

# Example 1: E. coli iML1515 model
ECOLI_IML1515_CONFIG = {
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
        "central_reactions": ["PGI", "PFK", "FBA", "TPI", "GAPD", "PGK", "PGM", "ENO", "PYK"],
        "perform_basic_info": True,
        "perform_fba": True,
        "perform_growth_analysis": True,
        "perform_environmental_analysis": True,
        "perform_essentiality_analysis": True,
        "create_visualizations": True
    }
}

# Example 2: Yeast model (S. cerevisiae)
YEAST_CONFIG = {
    "model_file_path": "models/yeast_model.xml",
    "output_directory": "results/yeast_analysis",
    "model_loading_options": {
        "model_format": "sbml",
        "preprocess_model": True,
        "remove_blocked_reactions": True,
        "set_objective": "BIOMASS_SC5_notrace"
    },
    "analysis_parameters": {
        "essentiality_threshold": 0.05,  # Higher threshold for yeast
        "carbon_sources": ["glucose", "ethanol", "glycerol"],
        "carbon_exchange_mapping": {
            "glucose": "EX_glc_e",
            "ethanol": "EX_etoh_e",
            "glycerol": "EX_glyc_e"
        },
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
        "central_reactions": ["HEX1", "PFK", "FBA", "TPI", "TDH1", "PGK", "PGM", "ENO", "PYK"],
        "perform_basic_info": True,
        "perform_fba": True,
        "perform_growth_analysis": True,
        "perform_environmental_analysis": False,  # Skip environmental analysis
        "perform_essentiality_analysis": True,
        "create_visualizations": True
    }
}

# Example 3: Minimal configuration for quick analysis
MINIMAL_CONFIG = {
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

# =============================================================================
# USAGE INSTRUCTIONS
# =============================================================================

"""
USAGE INSTRUCTIONS:

1. Copy this configuration file and modify the values according to your needs.

2. Replace the slot values in the main template file:
   - Replace {{model_file_path}} with your model path
   - Replace {{output_directory}} with your output directory
   - Replace {{essentiality_threshold}} with your threshold value
   - Replace {{carbon_sources}} with your carbon sources list
   - And so on for all other slots...

3. Example slot replacement:
   Original: MODEL_FILE_PATH = "{{model_file_path}}"
   Modified: MODEL_FILE_PATH = "models/my_model.xml"

4. Run the analysis:
   python constraint_based_analysis_template.py

5. Check the results in your output directory.

COMMON SLOT REPLACEMENTS:

For model file path:
- SBML format: "path/to/model.xml"
- JSON format: "path/to/model.json"  
- MATLAB format: "path/to/model.mat"

For carbon sources:
- ["glucose", "fructose", "acetate"]
- ["glucose", "ethanol", "glycerol"]
- ["glucose"]  # Single carbon source

For essentiality threshold:
- 0.01  # 1% of wild-type growth
- 0.05  # 5% of wild-type growth
- 0.1   # 10% of wild-type growth

For analysis options:
- True   # Perform this analysis
- False  # Skip this analysis
"""

if __name__ == "__main__":
    print("Configuration template loaded.")
    print("Modify the values above and use them to replace slots in the main template.")
