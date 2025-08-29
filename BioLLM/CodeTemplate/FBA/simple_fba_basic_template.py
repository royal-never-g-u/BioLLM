"""
Simple Basic FBA Analysis Template
This is a simplified template focused on basic FBA functionality without complex sensitivity analysis.
"""

import os
import urllib.request
import gzip
import cobra
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# AGENT SLOTS - Replace these values as needed
# =============================================================================

# SLOT: Model configuration
MODEL_URL = "{{MODEL_URL}}"  # e.g., "http://bigg.ucsd.edu/static/models/iML1515.xml.gz"
MODEL_NAME = "{{MODEL_NAME}}"  # e.g., "iML1515"
BIOMASS_REACTION_ID = "{{BIOMASS_REACTION_ID}}"  # e.g., "BIOMASS_Ec_iML1515_core_75p37M"

# SLOT: Output directory
OUTPUT_DIR = "{{OUTPUT_DIR}}"  # e.g., "/tmp/fba_analysis"

# SLOT: Analysis parameters
FLUX_THRESHOLD = "{{FLUX_THRESHOLD}}"  # e.g., 0.001

# =============================================================================
# DEFAULT VALUES (used if slots are not replaced)
# =============================================================================

# Apply defaults if slots are not filled
if MODEL_URL == "{{MODEL_URL}}":
    MODEL_URL = "http://bigg.ucsd.edu/static/models/iML1515.xml.gz"
if MODEL_NAME == "{{MODEL_NAME}}":
    MODEL_NAME = "iML1515"
if BIOMASS_REACTION_ID == "{{BIOMASS_REACTION_ID}}":
    BIOMASS_REACTION_ID = "BIOMASS_Ec_iML1515_core_75p37M"
if OUTPUT_DIR == "{{OUTPUT_DIR}}":
    OUTPUT_DIR = "/tmp/fba_analysis"
if FLUX_THRESHOLD == "{{FLUX_THRESHOLD}}":
    FLUX_THRESHOLD = 0.001

# =============================================================================
# MAIN ANALYSIS FUNCTIONS
# =============================================================================

def download_and_load_model():
    """Download and load the metabolic model"""
    print(f"Downloading {MODEL_NAME} model...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model_gz_path = os.path.join(OUTPUT_DIR, f"{MODEL_NAME}.xml.gz")
    model_path = os.path.join(OUTPUT_DIR, f"{MODEL_NAME}.xml")
    
    try:
        urllib.request.urlretrieve(MODEL_URL, model_gz_path)
        print(f"Downloaded model to: {model_gz_path}")
        
        with gzip.open(model_gz_path, 'rb') as f_in:
            with open(model_path, 'wb') as f_out:
                f_out.write(f_in.read())
        
        model = cobra.io.read_sbml_model(model_path)
        print(f"Model loaded successfully!")
        print(f"Model ID: {model.id}")
        print(f"Reactions: {len(model.reactions)}")
        print(f"Metabolites: {len(model.metabolites)}")
        print(f"Genes: {len(model.genes)}")
        
        return model
        
    except Exception as e:
        print(f"Error loading model: {e}")
        # Try uncompressed version
        try:
            model_url_alt = MODEL_URL.replace('.gz', '')
            urllib.request.urlretrieve(model_url_alt, model_path)
            model = cobra.io.read_sbml_model(model_path)
            print(f"Model loaded via alternative method!")
            return model
        except Exception as e2:
            print(f"Alternative loading failed: {e2}")
            raise

def perform_fba(model):
    """Perform basic FBA analysis"""
    print("Performing FBA analysis...")
    
    solution = model.optimize()
    print(f"FBA Status: {solution.status}")
    print(f"Growth Rate: {solution.objective_value:.6f} h⁻¹")
    
    if solution.status == 'optimal':
        # Get flux values
        flux_df = pd.DataFrame({
            'Reaction_ID': [rxn.id for rxn in model.reactions],
            'Reaction_Name': [rxn.name for rxn in model.reactions],
            'Flux_Value': [solution.fluxes[rxn.id] for rxn in model.reactions]
        })
        
        # Save results
        flux_file = os.path.join(OUTPUT_DIR, "flux_distribution.csv")
        flux_df.to_csv(flux_file, index=False)
        print(f"Flux distribution saved to: {flux_file}")
        
        # Show top fluxes
        top_fluxes = flux_df[flux_df['Flux_Value'] != 0].copy()
        top_fluxes['Abs_Flux'] = abs(top_fluxes['Flux_Value'])
        top_fluxes = top_fluxes.nlargest(10, 'Abs_Flux')
        print(f"\nTop 10 reactions with highest flux:")
        print(top_fluxes[['Reaction_ID', 'Reaction_Name', 'Flux_Value']].to_string(index=False))
        
        return solution, flux_df
    else:
        print(f"FBA failed with status: {solution.status}")
        return None, None

def analyze_flux_distributions(flux_df):
    """Analyze flux distributions and key pathways"""
    print("Analyzing flux distributions...")
    
    # Filter for reactions with significant flux
    significant_fluxes = flux_df[abs(flux_df['Flux_Value']) > FLUX_THRESHOLD].copy()
    significant_fluxes['Abs_Flux'] = abs(significant_fluxes['Flux_Value'])
    
    print(f"Number of reactions with significant flux (>{FLUX_THRESHOLD}): {len(significant_fluxes)}")
    
    # Categorize reactions by type
    def categorize_reaction(reaction_id):
        if 'EX_' in reaction_id:
            return 'Exchange'
        elif any(x in reaction_id for x in ['pp', 'ex', 't']):
            return 'Transport'
        elif 'BIOMASS' in reaction_id:
            return 'Biomass'
        elif any(x in reaction_id for x in ['ATPS', 'NADH', 'CYTBO']):
            return 'Energy'
        elif any(x in reaction_id for x in ['PYK', 'PGI', 'FBP', 'GAPD', 'PGK', 'PGM', 'ENO']):
            return 'Glycolysis'
        elif any(x in reaction_id for x in ['PDH', 'CS', 'AKGDH', 'SUCOAS', 'FUM', 'MDH']):
            return 'TCA_Cycle'
        elif any(x in reaction_id for x in ['G6PDH2r', 'PGL', 'GND', 'RPE', 'RPI']):
            return 'Pentose_Phosphate'
        else:
            return 'Other_Metabolic'
    
    significant_fluxes['Category'] = significant_fluxes['Reaction_ID'].apply(categorize_reaction)
    
    # Summarize by category
    category_summary = significant_fluxes.groupby('Category').agg({
        'Reaction_ID': 'count',
        'Abs_Flux': ['mean', 'sum', 'max']
    }).round(4)
    
    print("\nFlux distribution by pathway category:")
    print(category_summary)
    
    # Identify key exchange reactions (uptake and secretion)
    exchange_reactions = significant_fluxes[significant_fluxes['Category'] == 'Exchange'].copy()
    exchange_reactions = exchange_reactions.sort_values('Flux_Value')
    
    uptake_reactions = exchange_reactions[exchange_reactions['Flux_Value'] < -0.01]
    secretion_reactions = exchange_reactions[exchange_reactions['Flux_Value'] > 0.01]
    
    print(f"\nMajor uptake reactions (negative flux):")
    print(uptake_reactions[['Reaction_ID', 'Flux_Value']].head(10).to_string(index=False))
    
    print(f"\nMajor secretion reactions (positive flux):")
    print(secretion_reactions[['Reaction_ID', 'Flux_Value']].head(10).to_string(index=False))
    
    # Save pathway analysis
    pathway_file = os.path.join(OUTPUT_DIR, "pathway_analysis.csv")
    significant_fluxes.to_csv(pathway_file, index=False)
    print(f"\nPathway analysis saved to: {pathway_file}")
    
    return significant_fluxes

def create_basic_visualizations(flux_df, significant_fluxes):
    """Create basic visualizations"""
    print("Creating basic visualizations...")
    
    try:
        # Create a simple figure with 2 subplots
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(f'{MODEL_NAME} Basic FBA Analysis Results', fontsize=16, fontweight='bold')
        
        # 1. Top flux values (bar plot)
        top_fluxes = significant_fluxes.nlargest(10, 'Abs_Flux')
        y_pos = range(len(top_fluxes))
        axes[0].barh(y_pos, top_fluxes['Flux_Value'], color='steelblue')
        axes[0].set_yticks(y_pos)
        axes[0].set_yticklabels(top_fluxes['Reaction_ID'], fontsize=8)
        axes[0].set_xlabel('Flux Value (mmol/gDW/h)')
        axes[0].set_title('Top 10 Reaction Fluxes')
        axes[0].grid(True, alpha=0.3, axis='x')
        
        # 2. Pathway distribution pie chart
        category_counts = significant_fluxes['Category'].value_counts()
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_counts)))
        axes[1].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%', 
                    colors=colors, startangle=90)
        axes[1].set_title('Active Reactions by Pathway Category')
        
        plt.tight_layout()
        plot_file = os.path.join(OUTPUT_DIR, "basic_fba_results.png")
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"Basic visualization saved to: {plot_file}")
        plt.close()
        
    except Exception as e:
        print(f"Could not create visualizations: {e}")

def main():
    """Main function to run the basic FBA analysis"""
    print("=" * 50)
    print(f"Basic FBA Analysis - {MODEL_NAME}")
    print("=" * 50)
    
    try:
        # Step 1: Load model
        model = download_and_load_model()
        
        # Step 2: Perform FBA
        solution, flux_df = perform_fba(model)
        
        if solution is None:
            print("FBA analysis failed. Exiting.")
            return
        
        # Step 3: Analyze flux distributions
        significant_fluxes = analyze_flux_distributions(flux_df)
        
        # Step 4: Create basic visualizations
        create_basic_visualizations(flux_df, significant_fluxes)
        
        print("\n" + "=" * 50)
        print("Basic FBA Analysis Completed Successfully!")
        print(f"Results saved in: {OUTPUT_DIR}")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error during FBA analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
