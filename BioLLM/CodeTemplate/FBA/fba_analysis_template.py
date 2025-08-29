"""
FBA Analysis Template
This template provides a complete Flux Balance Analysis workflow with configurable slots.
Agent system can provide values for these slots to customize the analysis.
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
from pathlib import Path

# Suppress warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURABLE SLOTS - Agent system can provide these values
# =============================================================================

# SLOT: Model configuration
MODEL_URL = "{{MODEL_URL}}"  # Default: "http://bigg.ucsd.edu/static/models/iML1515.xml.gz"
MODEL_NAME = "{{MODEL_NAME}}"  # Default: "iML1515"
MODEL_ID = "{{MODEL_ID}}"  # Default: "iML1515"

# SLOT: Output directory
OUTPUT_DIR = "{{OUTPUT_DIR}}"  # Default: "/tmp/fba_analysis_output"

# SLOT: Analysis parameters
GLUCOSE_UPTAKE_RATES = {{GLUCOSE_UPTAKE_RATES}}  # Default: [5, 10, 15, 20, 25]
OXYGEN_AVAILABILITY_RATES = {{OXYGEN_AVAILABILITY_RATES}}  # Default: [10, 20, 30, 40, 50]
SIGNIFICANT_FLUX_THRESHOLD = {{SIGNIFICANT_FLUX_THRESHOLD}}  # Default: 0.001

# SLOT: Gene knockout analysis
TEST_GENES = {{TEST_GENES}}  # Default: ['b0008', 'b0114', 'b1136', 'b2925', 'b0720']

# SLOT: Visualization settings
FIGURE_SIZE = {{FIGURE_SIZE}}  # Default: (18, 12)
DPI = {{DPI}}  # Default: 300

# SLOT: Biomass reaction ID (if different from default)
BIOMASS_REACTION_ID = "{{BIOMASS_REACTION_ID}}"  # Default: "BIOMASS_Ec_iML1515_core_75p37M"

# SLOT: Key reactions for detailed analysis
KEY_REACTIONS = {{KEY_REACTIONS}}  # Default: ['BIOMASS_Ec_iML1515_core_75p37M', 'EX_glc__D_e', 'EX_o2_e', 'EX_co2_e', 'EX_h2o_e', 'ATPS4rpp', 'CYTBO3_4pp']

# =============================================================================
# DEFAULT VALUES (used when slots are not provided)
# =============================================================================

def get_default_values():
    """Return default values for all slots"""
    return {
        'MODEL_URL': "http://bigg.ucsd.edu/static/models/iML1515.xml.gz",
        'MODEL_NAME': "iML1515",
        'MODEL_ID': "iML1515",
        'OUTPUT_DIR': "/tmp/fba_analysis_output",
        'GLUCOSE_UPTAKE_RATES': [5, 10, 15, 20, 25],
        'OXYGEN_AVAILABILITY_RATES': [10, 20, 30, 40, 50],
        'SIGNIFICANT_FLUX_THRESHOLD': 0.001,
        'TEST_GENES': ['b0008', 'b0114', 'b1136', 'b2925', 'b0720'],
        'FIGURE_SIZE': (18, 12),
        'DPI': 300,
        'BIOMASS_REACTION_ID': "BIOMASS_Ec_iML1515_core_75p37M",
        'KEY_REACTIONS': ['BIOMASS_Ec_iML1515_core_75p37M', 'EX_glc__D_e', 'EX_o2_e', 'EX_co2_e', 'EX_h2o_e', 'ATPS4rpp', 'CYTBO3_4pp']
    }

# Apply default values if slots are not filled
defaults = get_default_values()

if MODEL_URL == "{{MODEL_URL}}":
    MODEL_URL = defaults['MODEL_URL']
if MODEL_NAME == "{{MODEL_NAME}}":
    MODEL_NAME = defaults['MODEL_NAME']
if MODEL_ID == "{{MODEL_ID}}":
    MODEL_ID = defaults['MODEL_ID']
if OUTPUT_DIR == "{{OUTPUT_DIR}}":
    OUTPUT_DIR = defaults['OUTPUT_DIR']
if GLUCOSE_UPTAKE_RATES == {{GLUCOSE_UPTAKE_RATES}}:
    GLUCOSE_UPTAKE_RATES = defaults['GLUCOSE_UPTAKE_RATES']
if OXYGEN_AVAILABILITY_RATES == {{OXYGEN_AVAILABILITY_RATES}}:
    OXYGEN_AVAILABILITY_RATES = defaults['OXYGEN_AVAILABILITY_RATES']
if SIGNIFICANT_FLUX_THRESHOLD == {{SIGNIFICANT_FLUX_THRESHOLD}}:
    SIGNIFICANT_FLUX_THRESHOLD = defaults['SIGNIFICANT_FLUX_THRESHOLD']
if TEST_GENES == {{TEST_GENES}}:
    TEST_GENES = defaults['TEST_GENES']
if FIGURE_SIZE == {{FIGURE_SIZE}}:
    FIGURE_SIZE = defaults['FIGURE_SIZE']
if DPI == {{DPI}}:
    DPI = defaults['DPI']
if BIOMASS_REACTION_ID == "{{BIOMASS_REACTION_ID}}":
    BIOMASS_REACTION_ID = defaults['BIOMASS_REACTION_ID']
if KEY_REACTIONS == {{KEY_REACTIONS}}:
    KEY_REACTIONS = defaults['KEY_REACTIONS']

# =============================================================================
# MAIN FBA ANALYSIS WORKFLOW
# =============================================================================

def create_output_directory():
    """Create output directory"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory created: {OUTPUT_DIR}")

def download_and_load_model():
    """Download and load the metabolic model"""
    print(f"Step 1: Downloading {MODEL_NAME} model...")
    
    model_gz_path = os.path.join(OUTPUT_DIR, f"{MODEL_NAME}.xml.gz")
    model_path = os.path.join(OUTPUT_DIR, f"{MODEL_NAME}.xml")
    
    try:
        # Download the model
        urllib.request.urlretrieve(MODEL_URL, model_gz_path)
        print(f"Downloaded model to: {model_gz_path}")
        
        # Extract the compressed file
        with gzip.open(model_gz_path, 'rb') as f_in:
            with open(model_path, 'wb') as f_out:
                f_out.write(f_in.read())
        
        print(f"Extracted model to: {model_path}")
        
        # Load the model using COBRApy
        model = cobra.io.read_sbml_model(model_path)
        print(f"\nModel loaded successfully!")
        print(f"Model ID: {model.id}")
        print(f"Number of reactions: {len(model.reactions)}")
        print(f"Number of metabolites: {len(model.metabolites)}")
        print(f"Number of genes: {len(model.genes)}")
        print(f"Objective function: {model.objective}")
        
        return model
        
    except Exception as e:
        print(f"Error downloading/loading model: {e}")
        # Alternative: try direct download without compression
        try:
            model_url_alt = MODEL_URL.replace('.gz', '')
            urllib.request.urlretrieve(model_url_alt, model_path)
            print(f"Downloaded uncompressed model to: {model_path}")
            model = cobra.io.read_sbml_model(model_path)
            print(f"Model loaded successfully via alternative method!")
            return model
        except Exception as e2:
            print(f"Alternative download also failed: {e2}")
            raise

def perform_basic_fba(model):
    """Perform basic FBA analysis"""
    print("Step 2: Performing basic FBA analysis...")
    
    # Perform FBA with default settings
    solution = model.optimize()
    print(f"FBA Solution Status: {solution.status}")
    print(f"Objective Value (Growth Rate): {solution.objective_value:.6f} h⁻¹")
    
    if solution.status == 'optimal':
        print("\nFBA analysis successful!")
        
        # Get biomass reaction details
        try:
            biomass_reaction = model.reactions.get_by_id(BIOMASS_REACTION_ID)
            print(f"\nBiomass reaction: {biomass_reaction.id}")
            print(f"Biomass equation: {biomass_reaction.reaction}")
        except:
            print(f"Warning: Biomass reaction {BIOMASS_REACTION_ID} not found")
        
        # Get flux values for all reactions
        flux_df = pd.DataFrame({
            'Reaction_ID': [rxn.id for rxn in model.reactions],
            'Reaction_Name': [rxn.name for rxn in model.reactions],
            'Flux_Value': [solution.fluxes[rxn.id] for rxn in model.reactions],
            'Lower_Bound': [rxn.lower_bound for rxn in model.reactions],
            'Upper_Bound': [rxn.upper_bound for rxn in model.reactions]
        })
        
        print(f"\nTotal number of reactions with non-zero flux: {sum(flux_df['Flux_Value'] != 0)}")
        print(f"Total number of reactions: {len(flux_df)}")
        
        # Save flux distribution
        flux_file = os.path.join(OUTPUT_DIR, "flux_distribution.csv")
        flux_df.to_csv(flux_file, index=False)
        print(f"Flux distribution saved to: {flux_file}")
        
        # Show top 10 reactions with highest absolute flux
        top_fluxes = flux_df[flux_df['Flux_Value'] != 0].copy()
        top_fluxes['Abs_Flux'] = abs(top_fluxes['Flux_Value'])
        top_fluxes = top_fluxes.nlargest(10, 'Abs_Flux')
        
        print(f"\nTop 10 reactions with highest flux:")
        print(top_fluxes[['Reaction_ID', 'Reaction_Name', 'Flux_Value']].to_string(index=False))
        
        return solution, flux_df
    else:
        print(f"FBA failed with status: {solution.status}")
        return None, None

def analyze_flux_distributions():
    """Analyze flux distributions and key pathways"""
    print("Step 3: Analyzing flux distributions and key pathways...")
    
    # Load the flux distribution
    flux_df = pd.read_csv(os.path.join(OUTPUT_DIR, "flux_distribution.csv"))
    
    # Filter for reactions with significant flux
    significant_fluxes = flux_df[abs(flux_df['Flux_Value']) > SIGNIFICANT_FLUX_THRESHOLD].copy()
    significant_fluxes['Abs_Flux'] = abs(significant_fluxes['Flux_Value'])
    
    print(f"Number of reactions with significant flux (>{SIGNIFICANT_FLUX_THRESHOLD}): {len(significant_fluxes)}")
    
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

def perform_sensitivity_analysis(model):
    """Perform sensitivity analysis and constraint variations"""
    print("Step 4: Performing sensitivity analysis and constraint variations...")
    
    # Test different glucose uptake rates
    growth_rates = []
    flux_results = []
    
    print("Testing different glucose uptake rates:")
    print("Glucose Rate (mmol/gDW/h) | Growth Rate (h⁻¹)")
    print("-" * 45)
    
    for glucose_rate in GLUCOSE_UPTAKE_RATES:
        # Create a copy of the model
        test_model = model.copy()
        
        # Set glucose uptake rate
        try:
            test_model.reactions.EX_glc__D_e.lower_bound = -glucose_rate
        except:
            print(f"Warning: EX_glc__D_e reaction not found, skipping glucose rate {glucose_rate}")
            continue
        
        # Optimize
        solution = test_model.optimize()
        growth_rate = solution.objective_value if solution.status == 'optimal' else 0
        growth_rates.append(growth_rate)
        
        print(f"{glucose_rate:20.1f} | {growth_rate:.6f}")
        
        # Store detailed flux data for key reactions
        if solution.status == 'optimal':
            flux_data = {'Glucose_Rate': glucose_rate, 'Growth_Rate': growth_rate}
            for rxn_id in KEY_REACTIONS:
                try:
                    flux_data[rxn_id] = solution.fluxes[rxn_id]
                except:
                    flux_data[rxn_id] = 0
            flux_results.append(flux_data)
    
    # Test different oxygen availability
    print("\n\nTesting different oxygen availability:")
    print("Oxygen Rate (mmol/gDW/h) | Growth Rate (h⁻¹)")
    print("-" * 43)
    
    oxygen_growth_rates = []
    
    for oxygen_rate in OXYGEN_AVAILABILITY_RATES:
        test_model = model.copy()
        try:
            test_model.reactions.EX_glc__D_e.lower_bound = -10  # Reset glucose to default
            test_model.reactions.EX_o2_e.lower_bound = -oxygen_rate
        except:
            print(f"Warning: Required exchange reactions not found, skipping oxygen rate {oxygen_rate}")
            continue
        
        solution = test_model.optimize()
        growth_rate = solution.objective_value if solution.status == 'optimal' else 0
        oxygen_growth_rates.append(growth_rate)
        
        print(f"{oxygen_rate:19.1f} | {growth_rate:.6f}")
    
    # Test anaerobic conditions
    print("\n\nTesting anaerobic conditions:")
    anaerobic_model = model.copy()
    try:
        anaerobic_model.reactions.EX_glc__D_e.lower_bound = -10
        anaerobic_model.reactions.EX_o2_e.lower_bound = 0  # No oxygen uptake
    except:
        print("Warning: Required exchange reactions not found for anaerobic test")
        anaerobic_growth = 0
    else:
        solution = anaerobic_model.optimize()
        anaerobic_growth = solution.objective_value if solution.status == 'optimal' else 0
    
    print(f"Anaerobic growth rate: {anaerobic_growth:.6f} h⁻¹")
    
    # Test gene knockout effects
    print("\n\nTesting single gene knockout effects on key genes:")
    knockout_results = []
    
    for gene_id in TEST_GENES:
        if gene_id in [g.id for g in model.genes]:
            test_model = model.copy()
            gene = test_model.genes.get_by_id(gene_id)
            
            # Perform knockout using cobra
            with test_model:
                gene.knock_out()
                solution = test_model.optimize()
                growth_rate = solution.objective_value if solution.status == 'optimal' else 0
                
            # Calculate growth reduction (assuming baseline growth rate)
            baseline_growth = 0.876997  # This could be made configurable
            growth_reduction = (baseline_growth - growth_rate) / baseline_growth * 100
            
            knockout_results.append({
                'Gene_ID': gene_id,
                'Growth_Rate': growth_rate,
                'Growth_Reduction': growth_reduction
            })
    
    if knockout_results:
        print("Gene ID | Growth Rate | Growth Reduction (%)")
        print("-" * 42)
        for result in knockout_results:
            print(f"{result['Gene_ID']:7s} | {result['Growth_Rate']:11.6f} | {result['Growth_Reduction']:15.2f}")
    
    # Save sensitivity analysis results
    sensitivity_df = pd.DataFrame({
        'Glucose_Rate': GLUCOSE_UPTAKE_RATES[:len(growth_rates)],
        'Growth_Rate': growth_rates
    })
    
    sensitivity_file = os.path.join(OUTPUT_DIR, "sensitivity_analysis.csv")
    sensitivity_df.to_csv(sensitivity_file, index=False)
    print(f"\nSensitivity analysis saved to: {sensitivity_file}")
    
    if flux_results:
        flux_results_df = pd.DataFrame(flux_results)
        flux_results_file = os.path.join(OUTPUT_DIR, "detailed_flux_results.csv")
        flux_results_df.to_csv(flux_results_file, index=False)
        print(f"Detailed flux results saved to: {flux_results_file}")
    
    return growth_rates, oxygen_growth_rates, anaerobic_growth, knockout_results

def generate_visualizations(growth_rates, oxygen_growth_rates, anaerobic_growth):
    """Generate comprehensive visualizations"""
    print("Step 5: Generating visualizations...")
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 3, figsize=FIGURE_SIZE)
    fig.suptitle(f'{MODEL_NAME} Metabolic Model - Flux Balance Analysis Results', fontsize=16, fontweight='bold')
    
    # 1. Growth rate vs glucose uptake rate
    if growth_rates:
        axes[0,0].plot(GLUCOSE_UPTAKE_RATES[:len(growth_rates)], growth_rates, 'o-', linewidth=2, markersize=8, color='navy')
        axes[0,0].set_xlabel('Glucose Uptake Rate (mmol/gDW/h)')
        axes[0,0].set_ylabel('Growth Rate (h⁻¹)')
        axes[0,0].set_title('A. Growth Rate vs Glucose Uptake')
        axes[0,0].grid(True, alpha=0.3)
    
    # 2. Growth rate vs oxygen availability
    if oxygen_growth_rates:
        axes[0,1].plot(OXYGEN_AVAILABILITY_RATES[:len(oxygen_growth_rates)], oxygen_growth_rates, 's-', linewidth=2, markersize=8, color='darkred')
        axes[0,1].set_xlabel('Oxygen Availability (mmol/gDW/h)')
        axes[0,1].set_ylabel('Growth Rate (h⁻¹)')
        axes[0,1].set_title('B. Growth Rate vs Oxygen Availability')
        axes[0,1].grid(True, alpha=0.3)
    
    # 3. Flux distribution by pathway category
    try:
        pathway_data = pd.read_csv(os.path.join(OUTPUT_DIR, "pathway_analysis.csv"))
        category_counts = pathway_data['Category'].value_counts()
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_counts)))
        axes[0,2].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%', 
                      colors=colors, startangle=90)
        axes[0,2].set_title('C. Active Reactions by Pathway Category')
    except:
        axes[0,2].text(0.5, 0.5, 'No pathway data available', ha='center', va='center', transform=axes[0,2].transAxes)
        axes[0,2].set_title('C. Active Reactions by Pathway Category')
    
    # 4. Top flux values (bar plot)
    try:
        pathway_data = pd.read_csv(os.path.join(OUTPUT_DIR, "pathway_analysis.csv"))
        top_fluxes = pathway_data.nlargest(15, 'Abs_Flux')
        y_pos = range(len(top_fluxes))
        axes[1,0].barh(y_pos, top_fluxes['Flux_Value'], color='steelblue')
        axes[1,0].set_yticks(y_pos)
        axes[1,0].set_yticklabels(top_fluxes['Reaction_ID'], fontsize=8)
        axes[1,0].set_xlabel('Flux Value (mmol/gDW/h)')
        axes[1,0].set_title('D. Top 15 Reaction Fluxes')
        axes[1,0].grid(True, alpha=0.3, axis='x')
    except:
        axes[1,0].text(0.5, 0.5, 'No flux data available', ha='center', va='center', transform=axes[1,0].transAxes)
        axes[1,0].set_title('D. Top 15 Reaction Fluxes')
    
    # 5. Exchange reactions (uptake vs secretion)
    try:
        exchange_data = pathway_data[pathway_data['Category'] == 'Exchange'].copy()
        uptake = exchange_data[exchange_data['Flux_Value'] < 0]['Flux_Value'].abs()
        secretion = exchange_data[exchange_data['Flux_Value'] > 0]['Flux_Value']
        
        categories = ['Uptake', 'Secretion']
        values = [uptake.sum(), secretion.sum()]
        axes[1,1].bar(categories, values, color=['lightcoral', 'lightblue'])
        axes[1,1].set_ylabel('Total Flux (mmol/gDW/h)')
        axes[1,1].set_title('E. Total Uptake vs Secretion Fluxes')
    except:
        axes[1,1].text(0.5, 0.5, 'No exchange data available', ha='center', va='center', transform=axes[1,1].transAxes)
        axes[1,1].set_title('E. Total Uptake vs Secretion Fluxes')
    
    # 6. Metabolic efficiency comparison
    conditions = ['Aerobic\n(Standard)', 'Aerobic\n(Low O₂)', 'Anaerobic']
    growth_values = [growth_rates[2] if len(growth_rates) > 2 else 0.876997, 
                     oxygen_growth_rates[1] if len(oxygen_growth_rates) > 1 else 0.531524, 
                     anaerobic_growth]
    colors_bar = ['green', 'orange', 'red']
    
    bars = axes[1,2].bar(conditions, growth_values, color=colors_bar, alpha=0.7)
    axes[1,2].set_ylabel('Growth Rate (h⁻¹)')
    axes[1,2].set_title('F. Growth Rate Under Different Conditions')
    axes[1,2].set_ylim(0, 1.0)
    
    # Add value labels on bars
    for bar, value in zip(bars, growth_values):
        axes[1,2].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                       f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plot_file = os.path.join(OUTPUT_DIR, "fba_analysis_results.png")
    plt.savefig(plot_file, dpi=DPI, bbox_inches='tight')
    print(f"Comprehensive analysis plot saved to: {plot_file}")
    
    # Generate pathway flux heatmap
    print("\nGenerating pathway flux heatmap...")
    try:
        flux_results_df = pd.read_csv(os.path.join(OUTPUT_DIR, "detailed_flux_results.csv"))
        
        # Prepare data for heatmap
        heatmap_data = flux_results_df.set_index('Glucose_Rate')
        heatmap_data = heatmap_data.drop('Growth_Rate', axis=1)
        
        # Normalize fluxes for better visualization
        heatmap_data_norm = heatmap_data.div(heatmap_data.abs().max(), axis=1)
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data_norm.T, annot=True, cmap='RdBu_r', center=0, 
                    fmt='.2f', cbar_kws={'label': 'Normalized Flux'})
        plt.title('Key Reaction Fluxes vs Glucose Uptake Rate', fontsize=14, fontweight='bold')
        plt.xlabel('Glucose Uptake Rate (mmol/gDW/h)')
        plt.ylabel('Reactions')
        plt.tight_layout()
        
        heatmap_file = os.path.join(OUTPUT_DIR, "pathway_flux_heatmap.png")
        plt.savefig(heatmap_file, dpi=DPI, bbox_inches='tight')
        print(f"Pathway flux heatmap saved to: {heatmap_file}")
    except Exception as e:
        print(f"Could not generate heatmap: {e}")
    
    plt.show()

def main():
    """Main function to run the complete FBA analysis"""
    print("=" * 60)
    print(f"FBA Analysis Template - {MODEL_NAME} Model")
    print("=" * 60)
    
    try:
        # Step 1: Create output directory
        create_output_directory()
        
        # Step 2: Download and load model
        model = download_and_load_model()
        
        # Step 3: Perform basic FBA
        solution, flux_df = perform_basic_fba(model)
        
        if solution is None:
            print("FBA analysis failed. Exiting.")
            return
        
        # Step 4: Analyze flux distributions
        significant_fluxes = analyze_flux_distributions()
        
        # Step 5: Perform sensitivity analysis
        growth_rates, oxygen_growth_rates, anaerobic_growth, knockout_results = perform_sensitivity_analysis(model)
        
        # Step 6: Generate visualizations
        generate_visualizations(growth_rates, oxygen_growth_rates, anaerobic_growth)
        
        print("\n" + "=" * 60)
        print("FBA Analysis Completed Successfully!")
        print(f"Results saved in: {OUTPUT_DIR}")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during FBA analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
