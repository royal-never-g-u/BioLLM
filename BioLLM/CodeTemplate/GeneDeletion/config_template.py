"""
Gene Deletion Analysis Configuration Template

This file contains all configurable parameters for the gene deletion analysis.
Agent systems can modify these values to customize the analysis.
"""

# =============================================================================
# MODEL CONFIGURATION SLOTS
# =============================================================================

# SLOT: Model loading configuration
MODEL_CONFIG = {
    "model_name": "iML1515",  # SLOT: Model name or path
    "model_type": "cobra",    # SLOT: Model type (cobra, sbml, etc.)
    "load_method": "load_model",  # SLOT: Loading method
    "model_description": "E. coli K-12 MG1655 metabolic model"  # SLOT: Model description
}

# SLOT: Analysis scope configuration
ANALYSIS_SCOPE = {
    "max_genes_to_analyze": 500,  # SLOT: Maximum number of genes to analyze
    "gene_selection_strategy": "representative",  # SLOT: Strategy for gene selection
    "focus_pathways": [  # SLOT: Pathways to focus on
        "glycolysis",
        "tca_cycle", 
        "fermentation",
        "amino_acid_metabolism"
    ],
    "exclude_essential_genes": True,  # SLOT: Whether to exclude essential genes
    "min_growth_rate_threshold": 0.1  # SLOT: Minimum growth rate threshold
}

# =============================================================================
# TARGET PRODUCT CONFIGURATION SLOTS
# =============================================================================

# SLOT: Target products for optimization
TARGET_PRODUCTS = {
    "EX_succ_e": {
        "name": "琥珀酸 (Succinate)",
        "priority": 1,
        "target_improvement": 10.0,  # SLOT: Target improvement percentage
        "min_production_rate": 5.0   # SLOT: Minimum production rate
    },
    "EX_lac__L_e": {
        "name": "L-乳酸 (L-Lactate)", 
        "priority": 2,
        "target_improvement": 15.0,
        "min_production_rate": 10.0
    },
    "EX_ac_e": {
        "name": "醋酸 (Acetate)",
        "priority": 3, 
        "target_improvement": 20.0,
        "min_production_rate": 15.0
    },
    "EX_etoh_e": {
        "name": "乙醇 (Ethanol)",
        "priority": 4,
        "target_improvement": 25.0,
        "min_production_rate": 12.0
    },
    "EX_for_e": {
        "name": "甲酸 (Formate)",
        "priority": 5,
        "target_improvement": 30.0,
        "min_production_rate": 50.0
    },
    "EX_pyr_e": {
        "name": "丙酮酸 (Pyruvate)",
        "priority": 6,
        "target_improvement": 18.0,
        "min_production_rate": 8.0
    }
}

# =============================================================================
# GENE KNOCKOUT STRATEGY SLOTS
# =============================================================================

# SLOT: Gene knockout effect classification
KNOCKOUT_EFFECT_CLASSIFICATION = {
    "lethal_threshold": 0.01,      # SLOT: Growth rate threshold for lethal effect
    "severe_effect_threshold": 0.1, # SLOT: Growth rate threshold for severe effect
    "moderate_effect_threshold": 0.8, # SLOT: Growth ratio threshold for moderate effect
    "mild_effect_threshold": 0.95,   # SLOT: Growth ratio threshold for mild effect
    "effect_categories": [          # SLOT: Effect category names
        "致死",
        "严重影响", 
        "中等影响",
        "轻微影响",
        "无影响"
    ]
}

# SLOT: Candidate gene selection criteria
CANDIDATE_GENE_CRITERIA = {
    "pathway_keywords": [  # SLOT: Keywords for pathway identification
        "pgi", "pfk", "fba", "tpi", "gapdh", "pyk", "eno",  # glycolysis
        "cs", "acont", "icd", "akgdh", "sucoas", "sdh", "fum", "mdh",  # TCA
        "ppc", "pck", "mae", "pps",  # PEP metabolism
        "ack", "pta", "ldh", "adh", "pfl"  # fermentation
    ],
    "max_candidates": 100,  # SLOT: Maximum number of candidate genes
    "include_transport_genes": True,  # SLOT: Whether to include transport genes
    "include_regulatory_genes": False  # SLOT: Whether to include regulatory genes
}

# =============================================================================
# OPTIMIZATION PARAMETERS SLOTS
# =============================================================================

# SLOT: Optimization constraints
OPTIMIZATION_CONSTRAINTS = {
    "min_biomass_rate": 0.05,  # SLOT: Minimum biomass production rate
    "max_biomass_rate": 0.9,   # SLOT: Maximum biomass production rate
    "glucose_uptake_rate": 10.0,  # SLOT: Glucose uptake rate constraint
    "oxygen_uptake_rate": 15.0,   # SLOT: Oxygen uptake rate constraint
    "maintenance_atp": 8.39       # SLOT: Maintenance ATP requirement
}

# SLOT: Production optimization settings
PRODUCTION_OPTIMIZATION = {
    "optimization_method": "FBA",  # SLOT: Optimization method (FBA, FVA, etc.)
    "objective_type": "maximize_production",  # SLOT: Objective type
    "couple_growth_production": True,  # SLOT: Whether to couple growth and production
    "production_yield_threshold": 0.1  # SLOT: Minimum production yield threshold
}

# =============================================================================
# VISUALIZATION CONFIGURATION SLOTS
# =============================================================================

# SLOT: Plot configuration
PLOT_CONFIG = {
    "figure_size": (16, 12),  # SLOT: Figure size (width, height)
    "dpi": 300,               # SLOT: DPI for saved figures
    "color_scheme": "Set3",   # SLOT: Color scheme for plots
    "font_family": "SimHei",  # SLOT: Font family for Chinese text
    "save_format": "png"      # SLOT: Save format (png, pdf, svg)
}

# SLOT: Chart types to generate
CHART_TYPES = {
    "product_comparison": True,      # SLOT: Generate product comparison chart
    "knockout_effects": True,        # SLOT: Generate knockout effects chart
    "gene_targets": True,            # SLOT: Generate gene targets chart
    "growth_production_tradeoff": True,  # SLOT: Generate tradeoff chart
    "pathway_analysis": False        # SLOT: Generate pathway analysis chart
}

# =============================================================================
# OUTPUT CONFIGURATION SLOTS
# =============================================================================

# SLOT: Output directory and file naming
OUTPUT_CONFIG = {
    "output_directory": "/tmp/gene_deletion_analysis",  # SLOT: Output directory
    "file_prefix": "gene_deletion",  # SLOT: File name prefix
    "include_timestamp": True,       # SLOT: Include timestamp in filenames
    "create_subdirectories": True    # SLOT: Create subdirectories for different outputs
}

# SLOT: Report generation settings
REPORT_CONFIG = {
    "generate_summary_report": True,     # SLOT: Generate summary report
    "generate_detailed_report": True,    # SLOT: Generate detailed report
    "generate_csv_results": True,        # SLOT: Generate CSV results
    "generate_json_results": False,      # SLOT: Generate JSON results
    "include_model_info": True,          # SLOT: Include model information
    "include_methodology": True,         # SLOT: Include methodology section
    "include_recommendations": True      # SLOT: Include recommendations
}

# =============================================================================
# CRISPR IMPLEMENTATION SLOTS
# =============================================================================

# SLOT: CRISPR implementation settings
CRISPR_CONFIG = {
    "target_organism": "E. coli",  # SLOT: Target organism
    "crispr_system": "CRISPR-Cas9",  # SLOT: CRISPR system to use
    "implementation_priority": "single_gene_first",  # SLOT: Implementation priority
    "max_genes_per_experiment": 3,  # SLOT: Maximum genes per experiment
    "include_control_strains": True,  # SLOT: Include control strains
    "validation_methods": [  # SLOT: Validation methods
        "PCR_verification",
        "growth_assay", 
        "product_quantification"
    ]
}

# =============================================================================
# EXPERIMENTAL VALIDATION SLOTS
# =============================================================================

# SLOT: Experimental validation parameters
EXPERIMENTAL_CONFIG = {
    "culture_medium": "M9_minimal",  # SLOT: Culture medium
    "temperature": 37,               # SLOT: Temperature in Celsius
    "ph": 7.0,                      # SLOT: pH value
    "aeration": "aerobic",           # SLOT: Aeration condition
    "sampling_timepoints": [2, 4, 6, 8, 12, 24],  # SLOT: Sampling timepoints (hours)
    "replicate_count": 3,            # SLOT: Number of replicates
    "analytical_methods": [          # SLOT: Analytical methods
        "HPLC",
        "GC-MS",
        "spectrophotometry"
    ]
}

# =============================================================================
# RISK ASSESSMENT SLOTS
# =============================================================================

# SLOT: Risk assessment parameters
RISK_ASSESSMENT = {
    "growth_rate_decline_threshold": 0.5,  # SLOT: Growth rate decline threshold
    "productivity_decline_threshold": 0.3,  # SLOT: Productivity decline threshold
    "lethality_risk_weight": 0.8,          # SLOT: Weight for lethality risk
    "productivity_risk_weight": 0.6,       # SLOT: Weight for productivity risk
    "experimental_risk_weight": 0.4        # SLOT: Weight for experimental risk
}

# =============================================================================
# TEMPLATE VALIDATION
# =============================================================================

def validate_config():
    """
    Validate the configuration parameters.
    Returns True if valid, raises ValueError if invalid.
    """
    # Validate model configuration
    if not MODEL_CONFIG["model_name"]:
        raise ValueError("Model name must be specified")
    
    # Validate analysis scope
    if ANALYSIS_SCOPE["max_genes_to_analyze"] <= 0:
        raise ValueError("max_genes_to_analyze must be positive")
    
    # Validate target products
    if not TARGET_PRODUCTS:
        raise ValueError("At least one target product must be specified")
    
    # Validate knockout effect classification
    if KNOCKOUT_EFFECT_CLASSIFICATION["lethal_threshold"] <= 0:
        raise ValueError("lethal_threshold must be positive")
    
    return True

# SLOT: Configuration validation on import
try:
    validate_config()
    print("✓ Configuration template loaded successfully")
except ValueError as e:
    print(f"⚠ Configuration validation warning: {e}")
