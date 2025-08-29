"""
FBA Template Configuration
This file contains all configurable slots for the FBA analysis template.
Agent system can modify these values to customize the analysis.
"""

# =============================================================================
# MODEL CONFIGURATION SLOTS
# =============================================================================

# SLOT: Model URL for download
MODEL_URL = "http://bigg.ucsd.edu/static/models/iML1515.xml.gz"

# SLOT: Model name for file naming and display
MODEL_NAME = "iML1515"

# SLOT: Model ID (usually same as MODEL_NAME)
MODEL_ID = "iML1515"

# SLOT: Biomass reaction ID (specific to the model)
BIOMASS_REACTION_ID = "BIOMASS_Ec_iML1515_core_75p37M"

# =============================================================================
# OUTPUT CONFIGURATION SLOTS
# =============================================================================

# SLOT: Output directory for all results
OUTPUT_DIR = "/tmp/fba_analysis_output"

# SLOT: Figure size for plots (width, height)
FIGURE_SIZE = (18, 12)

# SLOT: DPI for saved figures
DPI = 300

# =============================================================================
# ANALYSIS PARAMETER SLOTS
# =============================================================================

# SLOT: Glucose uptake rates to test (mmol/gDW/h)
GLUCOSE_UPTAKE_RATES = [5, 10, 15, 20, 25]

# SLOT: Oxygen availability rates to test (mmol/gDW/h)
OXYGEN_AVAILABILITY_RATES = [10, 20, 30, 40, 50]

# SLOT: Threshold for significant flux values
SIGNIFICANT_FLUX_THRESHOLD = 0.001

# =============================================================================
# GENE ANALYSIS SLOTS
# =============================================================================

# SLOT: Genes to test for knockout analysis
TEST_GENES = ['b0008', 'b0114', 'b1136', 'b2925', 'b0720']

# =============================================================================
# REACTION ANALYSIS SLOTS
# =============================================================================

# SLOT: Key reactions to track in detailed analysis
KEY_REACTIONS = [
    'BIOMASS_Ec_iML1515_core_75p37M',  # Biomass reaction
    'EX_glc__D_e',                     # Glucose exchange
    'EX_o2_e',                         # Oxygen exchange
    'EX_co2_e',                        # CO2 exchange
    'EX_h2o_e',                        # Water exchange
    'ATPS4rpp',                        # ATP synthase
    'CYTBO3_4pp'                       # Cytochrome oxidase
]

# =============================================================================
# PATHWAY CATEGORIZATION SLOTS
# =============================================================================

# SLOT: Reaction patterns for pathway categorization
PATHWAY_PATTERNS = {
    'Exchange': ['EX_'],
    'Transport': ['pp', 'ex', 't'],
    'Biomass': ['BIOMASS'],
    'Energy': ['ATPS', 'NADH', 'CYTBO'],
    'Glycolysis': ['PYK', 'PGI', 'FBP', 'GAPD', 'PGK', 'PGM', 'ENO'],
    'TCA_Cycle': ['PDH', 'CS', 'AKGDH', 'SUCOAS', 'FUM', 'MDH'],
    'Pentose_Phosphate': ['G6PDH2r', 'PGL', 'GND', 'RPE', 'RPI']
}

# =============================================================================
# VISUALIZATION SLOTS
# =============================================================================

# SLOT: Color scheme for plots
COLOR_SCHEME = {
    'growth_curve': 'navy',
    'oxygen_curve': 'darkred',
    'flux_bars': 'steelblue',
    'uptake': 'lightcoral',
    'secretion': 'lightblue',
    'conditions': ['green', 'orange', 'red']
}

# SLOT: Plot titles and labels
PLOT_LABELS = {
    'main_title': 'Metabolic Model - Flux Balance Analysis Results',
    'growth_vs_glucose': 'Growth Rate vs Glucose Uptake',
    'growth_vs_oxygen': 'Growth Rate vs Oxygen Availability',
    'pathway_distribution': 'Active Reactions by Pathway Category',
    'top_fluxes': 'Top 15 Reaction Fluxes',
    'exchange_fluxes': 'Total Uptake vs Secretion Fluxes',
    'condition_comparison': 'Growth Rate Under Different Conditions'
}

# =============================================================================
# VALIDATION SLOTS
# =============================================================================

# SLOT: Required reactions that must exist in the model
REQUIRED_REACTIONS = [
    'EX_glc__D_e',  # Glucose exchange
    'EX_o2_e'       # Oxygen exchange
]

# SLOT: Baseline growth rate for knockout analysis
BASELINE_GROWTH_RATE = 0.876997

# =============================================================================
# ERROR HANDLING SLOTS
# =============================================================================

# SLOT: Whether to continue analysis if some reactions are missing
CONTINUE_ON_MISSING_REACTIONS = True

# SLOT: Whether to show warnings for missing reactions
SHOW_MISSING_REACTION_WARNINGS = True

# =============================================================================
# PERFORMANCE SLOTS
# =============================================================================

# SLOT: Maximum number of reactions to display in top fluxes
MAX_TOP_FLUXES = 15

# SLOT: Maximum number of exchange reactions to display
MAX_EXCHANGE_REACTIONS = 10

# SLOT: Whether to save intermediate results
SAVE_INTERMEDIATE_RESULTS = True

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def validate_config():
    """Validate the configuration parameters"""
    errors = []
    
    # Check if OUTPUT_DIR is writable
    try:
        import os
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        test_file = os.path.join(OUTPUT_DIR, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
    except Exception as e:
        errors.append(f"OUTPUT_DIR is not writable: {e}")
    
    # Check if MODEL_URL is accessible
    try:
        import urllib.request
        urllib.request.urlopen(MODEL_URL, timeout=10)
    except Exception as e:
        errors.append(f"MODEL_URL is not accessible: {e}")
    
    # Check if lists are not empty
    if not GLUCOSE_UPTAKE_RATES:
        errors.append("GLUCOSE_UPTAKE_RATES cannot be empty")
    if not OXYGEN_AVAILABILITY_RATES:
        errors.append("OXYGEN_AVAILABILITY_RATES cannot be empty")
    if not KEY_REACTIONS:
        errors.append("KEY_REACTIONS cannot be empty")
    
    # Check if threshold is positive
    if SIGNIFICANT_FLUX_THRESHOLD <= 0:
        errors.append("SIGNIFICANT_FLUX_THRESHOLD must be positive")
    
    return errors

def get_config_summary():
    """Return a summary of the current configuration"""
    return {
        'model': {
            'url': MODEL_URL,
            'name': MODEL_NAME,
            'id': MODEL_ID,
            'biomass_reaction': BIOMASS_REACTION_ID
        },
        'output': {
            'directory': OUTPUT_DIR,
            'figure_size': FIGURE_SIZE,
            'dpi': DPI
        },
        'analysis': {
            'glucose_rates': GLUCOSE_UPTAKE_RATES,
            'oxygen_rates': OXYGEN_AVAILABILITY_RATES,
            'flux_threshold': SIGNIFICANT_FLUX_THRESHOLD,
            'test_genes': TEST_GENES,
            'key_reactions': KEY_REACTIONS
        },
        'validation_errors': validate_config()
    }

if __name__ == "__main__":
    # Print configuration summary when run directly
    summary = get_config_summary()
    print("FBA Template Configuration Summary:")
    print("=" * 50)
    
    for section, config in summary.items():
        if section != 'validation_errors':
            print(f"\n{section.upper()}:")
            for key, value in config.items():
                print(f"  {key}: {value}")
    
    errors = summary['validation_errors']
    if errors:
        print(f"\nVALIDATION ERRORS:")
        for error in errors:
            print(f"  - {error}")
    else:
        print(f"\nConfiguration is valid!")
