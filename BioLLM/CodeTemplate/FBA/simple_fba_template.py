"""
Simple FBA Analysis Template
This is a simplified template with clear slots for agent system to replace.
All slots are marked with {{SLOT_NAME}} format for easy identification and replacement.
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
GLUCOSE_RATES = "{{GLUCOSE_RATES}}"  # e.g., [5, 10, 15, 20, 25]
OXYGEN_RATES = "{{OXYGEN_RATES}}"  # e.g., [10, 20, 30, 40, 50]
FLUX_THRESHOLD = "{{FLUX_THRESHOLD}}"  # e.g., 0.001

# SLOT: Genes to test
TEST_GENES = "{{TEST_GENES}}"  # e.g., ['b0008', 'b0114', 'b1136']

# SLOT: Key reactions to track
KEY_REACTIONS = "{{KEY_REACTIONS}}"  # e.g., ['BIOMASS_Ec_iML1515_core_75p37M', 'EX_glc__D_e', 'EX_o2_e']

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

# Handle list and numeric slots with string comparison
# Check if variables are still placeholder strings and set defaults
if GLUCOSE_RATES == "{{GLUCOSE_RATES}}":
    GLUCOSE_RATES = [5, 10, 15, 20, 25]

if OXYGEN_RATES == "{{OXYGEN_RATES}}":
    OXYGEN_RATES = [10, 20, 30, 40, 50]

if FLUX_THRESHOLD == "{{FLUX_THRESHOLD}}":
    FLUX_THRESHOLD = 0.001

if TEST_GENES == "{{TEST_GENES}}":
    TEST_GENES = ['b0008', 'b0114', 'b1136']

if KEY_REACTIONS == "{{KEY_REACTIONS}}":
    KEY_REACTIONS = ['BIOMASS_Ec_iML1515_core_75p37M', 'EX_glc__D_e', 'EX_o2_e']

# =============================================================================
# MAIN ANALYSIS FUNCTIONS
# =============================================================================

def download_and_load_model():
    """Download and load the metabolic model"""
    print(f"Loading {MODEL_NAME} model...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Check if we have a local model file
    local_model_path = "../downloads/e_coli_core.mat"
    if os.path.exists(local_model_path):
        try:
            print(f"Loading local model from: {local_model_path}")
            model = cobra.io.load_matlab_model(local_model_path)
            print(f"Model loaded successfully!")
            print(f"Model ID: {model.id}")
            print(f"Reactions: {len(model.reactions)}")
            print(f"Metabolites: {len(model.metabolites)}")
            print(f"Genes: {len(model.genes)}")
            return model
        except Exception as e:
            print(f"Error loading local model: {e}")
    
    # Fallback to downloading from URL
    try:
        model_gz_path = os.path.join(OUTPUT_DIR, f"{MODEL_NAME}.xml.gz")
        model_path = os.path.join(OUTPUT_DIR, f"{MODEL_NAME}.xml")
        
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

def sensitivity_analysis(model):
    """Perform sensitivity analysis"""
    print("Performing sensitivity analysis...")
    
    # Test glucose uptake rates
    growth_rates = []
    print("Testing glucose uptake rates:")
    print("Glucose Rate | Growth Rate")
    print("-" * 25)
    
    for glucose_rate in GLUCOSE_RATES:
        try:
            # Use a safer approach for model modification
            test_model = model.copy()
            
            # Set glucose uptake rate
            if 'EX_glc__D_e' in test_model.reactions:
                test_model.reactions.EX_glc__D_e.lower_bound = -glucose_rate
                solution = test_model.optimize()
                growth_rate = solution.objective_value if solution.status == 'optimal' else 0
                growth_rates.append(growth_rate)
                print(f"{glucose_rate:11.1f} | {growth_rate:.6f}")
            else:
                print(f"{glucose_rate:11.1f} | EX_glc__D_e not found")
                growth_rates.append(0)
        except Exception as e:
            print(f"{glucose_rate:11.1f} | Failed: {str(e)[:50]}")
            # Try alternative approach without copying
            try:
                # Modify the original model temporarily
                original_lb = model.reactions.EX_glc__D_e.lower_bound
                model.reactions.EX_glc__D_e.lower_bound = -glucose_rate
                solution = model.optimize()
                growth_rate = solution.objective_value if solution.status == 'optimal' else 0
                growth_rates.append(growth_rate)
                print(f"{glucose_rate:11.1f} | {growth_rate:.6f} (alt)")
                # Restore original bounds
                model.reactions.EX_glc__D_e.lower_bound = original_lb
            except:
                print(f"{glucose_rate:11.1f} | Failed completely")
                growth_rates.append(0)
    
    # Test oxygen availability
    oxygen_growth_rates = []
    print("\nTesting oxygen availability:")
    print("Oxygen Rate | Growth Rate")
    print("-" * 25)
    
    for oxygen_rate in OXYGEN_RATES:
        try:
            # Use a safer approach for model modification
            test_model = model.copy()
            
            # Set glucose and oxygen uptake rates
            if 'EX_glc__D_e' in test_model.reactions and 'EX_o2_e' in test_model.reactions:
                test_model.reactions.EX_glc__D_e.lower_bound = -10
                test_model.reactions.EX_o2_e.lower_bound = -oxygen_rate
                solution = test_model.optimize()
                growth_rate = solution.objective_value if solution.status == 'optimal' else 0
                oxygen_growth_rates.append(growth_rate)
                print(f"{oxygen_rate:10.1f} | {growth_rate:.6f}")
            else:
                print(f"{oxygen_rate:10.1f} | Required reactions not found")
                oxygen_growth_rates.append(0)
        except Exception as e:
            print(f"{oxygen_rate:10.1f} | Failed: {str(e)[:50]}")
            # Try alternative approach without copying
            try:
                # Modify the original model temporarily
                original_glc_lb = model.reactions.EX_glc__D_e.lower_bound
                original_o2_lb = model.reactions.EX_o2_e.lower_bound
                model.reactions.EX_glc__D_e.lower_bound = -10
                model.reactions.EX_o2_e.lower_bound = -oxygen_rate
                solution = model.optimize()
                growth_rate = solution.objective_value if solution.status == 'optimal' else 0
                oxygen_growth_rates.append(growth_rate)
                print(f"{oxygen_rate:10.1f} | {growth_rate:.6f} (alt)")
                # Restore original bounds
                model.reactions.EX_glc__D_e.lower_bound = original_glc_lb
                model.reactions.EX_o2_e.lower_bound = original_o2_lb
            except:
                print(f"{oxygen_rate:10.1f} | Failed completely")
                oxygen_growth_rates.append(0)
    
    # Test anaerobic conditions
    try:
        # Use a safer approach for model modification
        anaerobic_model = model.copy()
        
        # Set anaerobic conditions
        if 'EX_glc__D_e' in anaerobic_model.reactions and 'EX_o2_e' in anaerobic_model.reactions:
            anaerobic_model.reactions.EX_glc__D_e.lower_bound = -10
            anaerobic_model.reactions.EX_o2_e.lower_bound = 0
            solution = anaerobic_model.optimize()
            anaerobic_growth = solution.objective_value if solution.status == 'optimal' else 0
        else:
            anaerobic_growth = 0
    except Exception as e:
        print(f"Anaerobic test failed: {str(e)[:50]}")
        # Try alternative approach without copying
        try:
            # Modify the original model temporarily
            original_glc_lb = model.reactions.EX_glc__D_e.lower_bound
            original_o2_lb = model.reactions.EX_o2_e.lower_bound
            model.reactions.EX_glc__D_e.lower_bound = -10
            model.reactions.EX_o2_e.lower_bound = 0
            solution = model.optimize()
            anaerobic_growth = solution.objective_value if solution.status == 'optimal' else 0
            # Restore original bounds
            model.reactions.EX_glc__D_e.lower_bound = original_glc_lb
            model.reactions.EX_o2_e.lower_bound = original_o2_lb
        except:
            anaerobic_growth = 0
    
    print(f"\nAnaerobic growth rate: {anaerobic_growth:.6f} h⁻¹")
    
    # Save results
    sensitivity_df = pd.DataFrame({
        'Glucose_Rate': GLUCOSE_RATES,
        'Growth_Rate': growth_rates
    })
    sensitivity_file = os.path.join(OUTPUT_DIR, "sensitivity_analysis.csv")
    sensitivity_df.to_csv(sensitivity_file, index=False)
    print(f"Sensitivity analysis saved to: {sensitivity_file}")
    
    return growth_rates, oxygen_growth_rates, anaerobic_growth

def gene_knockout_analysis(model):
    """Perform gene knockout analysis"""
    print("Performing gene knockout analysis...")
    
    knockout_results = []
    print("Gene ID | Growth Rate | Growth Reduction (%)")
    print("-" * 42)
    
    # Get baseline growth rate from the original model
    baseline_solution = model.optimize()
    baseline_growth = baseline_solution.objective_value if baseline_solution.status == 'optimal' else 0.876997
    
    for gene_id in TEST_GENES:
        try:
            if gene_id in [g.id for g in model.genes]:
                # Use a safer approach for model modification
                test_model = model.copy()
                
                if gene_id in [g.id for g in test_model.genes]:
                    gene = test_model.genes.get_by_id(gene_id)
                    
                    with test_model:
                        gene.knock_out()
                        solution = test_model.optimize()
                        growth_rate = solution.objective_value if solution.status == 'optimal' else 0
                    
                    growth_reduction = (baseline_growth - growth_rate) / baseline_growth * 100
                    
                    knockout_results.append({
                        'Gene_ID': gene_id,
                        'Growth_Rate': growth_rate,
                        'Growth_Reduction': growth_reduction
                    })
                    
                    print(f"{gene_id:7s} | {growth_rate:11.6f} | {growth_reduction:15.2f}")
                else:
                    print(f"{gene_id:7s} | Gene not found in model")
            else:
                print(f"{gene_id:7s} | Gene not found in original model")
        except Exception as e:
            print(f"{gene_id:7s} | Failed: {str(e)[:30]}")
            # Try alternative approach without copying
            try:
                if gene_id in [g.id for g in model.genes]:
                    gene = model.genes.get_by_id(gene_id)
                    
                    with model:
                        gene.knock_out()
                        solution = model.optimize()
                        growth_rate = solution.objective_value if solution.status == 'optimal' else 0
                    
                    growth_reduction = (baseline_growth - growth_rate) / baseline_growth * 100
                    
                    knockout_results.append({
                        'Gene_ID': gene_id,
                        'Growth_Rate': growth_rate,
                        'Growth_Reduction': growth_reduction
                    })
                    
                    print(f"{gene_id:7s} | {growth_rate:11.6f} | {growth_reduction:15.2f} (alt)")
                else:
                    print(f"{gene_id:7s} | Gene not found")
            except:
                print(f"{gene_id:7s} | Failed completely")
    
    return knockout_results

def create_visualizations(growth_rates, oxygen_growth_rates, anaerobic_growth):
    """Create visualizations"""
    print("Creating visualizations...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'{MODEL_NAME} FBA Analysis Results', fontsize=16, fontweight='bold')
    
    # Growth rate vs glucose uptake
    if growth_rates:
        axes[0,0].plot(GLUCOSE_RATES[:len(growth_rates)], growth_rates, 'o-', linewidth=2, markersize=8, color='navy')
        axes[0,0].set_xlabel('Glucose Uptake Rate (mmol/gDW/h)')
        axes[0,0].set_ylabel('Growth Rate (h⁻¹)')
        axes[0,0].set_title('Growth Rate vs Glucose Uptake')
        axes[0,0].grid(True, alpha=0.3)
    
    # Growth rate vs oxygen availability
    if oxygen_growth_rates:
        axes[0,1].plot(OXYGEN_RATES[:len(oxygen_growth_rates)], oxygen_growth_rates, 's-', linewidth=2, markersize=8, color='darkred')
        axes[0,1].set_xlabel('Oxygen Availability (mmol/gDW/h)')
        axes[0,1].set_ylabel('Growth Rate (h⁻¹)')
        axes[0,1].set_title('Growth Rate vs Oxygen Availability')
        axes[0,1].grid(True, alpha=0.3)
    
    # Load flux data for pathway analysis
    try:
        flux_df = pd.read_csv(os.path.join(OUTPUT_DIR, "flux_distribution.csv"))
        significant_fluxes = flux_df[abs(flux_df['Flux_Value']) > FLUX_THRESHOLD].copy()
        
        # Categorize reactions
        def categorize_reaction(reaction_id):
            if 'EX_' in reaction_id:
                return 'Exchange'
            elif 'BIOMASS' in reaction_id:
                return 'Biomass'
            elif any(x in reaction_id for x in ['ATPS', 'NADH', 'CYTBO']):
                return 'Energy'
            elif any(x in reaction_id for x in ['PYK', 'PGI', 'FBP', 'GAPD']):
                return 'Glycolysis'
            elif any(x in reaction_id for x in ['PDH', 'CS', 'AKGDH', 'SUCOAS']):
                return 'TCA_Cycle'
            else:
                return 'Other'
        
        significant_fluxes['Category'] = significant_fluxes['Reaction_ID'].apply(categorize_reaction)
        category_counts = significant_fluxes['Category'].value_counts()
        
        # Pathway distribution pie chart
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_counts)))
        axes[1,0].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%', 
                      colors=colors, startangle=90)
        axes[1,0].set_title('Active Reactions by Pathway Category')
        
        # Top flux values
        top_fluxes = significant_fluxes.nlargest(10, 'Flux_Value')
        y_pos = range(len(top_fluxes))
        axes[1,1].barh(y_pos, top_fluxes['Flux_Value'], color='steelblue')
        axes[1,1].set_yticks(y_pos)
        axes[1,1].set_yticklabels(top_fluxes['Reaction_ID'], fontsize=8)
        axes[1,1].set_xlabel('Flux Value (mmol/gDW/h)')
        axes[1,1].set_title('Top 10 Reaction Fluxes')
        axes[1,1].grid(True, alpha=0.3, axis='x')
        
    except Exception as e:
        print(f"Could not create pathway visualizations: {e}")
        axes[1,0].text(0.5, 0.5, 'No pathway data', ha='center', va='center', transform=axes[1,0].transAxes)
        axes[1,1].text(0.5, 0.5, 'No flux data', ha='center', va='center', transform=axes[1,1].transAxes)
    
    plt.tight_layout()
    plot_file = os.path.join(OUTPUT_DIR, "fba_results.png")
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"Visualization saved to: {plot_file}")
    plt.show()

def save_analysis_results(model, solution, flux_df, growth_rates, oxygen_growth_rates, anaerobic_growth, knockout_results):
    """
    Save analysis results to JSON file for later processing
    
    Args:
        model: cobra.Model object
        solution: FBA solution
        flux_df: Flux distribution DataFrame
        growth_rates: Glucose sensitivity growth rates
        oxygen_growth_rates: Oxygen sensitivity growth rates
        anaerobic_growth: Anaerobic growth rate
        knockout_results: Gene knockout analysis results
    """
    import json
    
    # Prepare analysis results
    analysis_results = {
        'model_info': {
            'model_id': model.id,
            'reactions_count': len(model.reactions),
            'metabolites_count': len(model.metabolites),
            'genes_count': len(model.genes)
        },
        'fba_analysis': {
            'objective_value': solution.objective_value if solution else 0,
            'status': solution.status if solution else 'Unknown',
            'flux_distribution': {}
        },
        'sensitivity_analysis': {
            'glucose_sensitivity': {},
            'oxygen_sensitivity': {},
            'anaerobic_growth': anaerobic_growth
        },
        'pathway_analysis': {
            'pathway_distribution': {}
        },
        'gene_knockout_analysis': {
            'knockout_results': knockout_results if knockout_results else []
        }
    }
    
    # Add flux distribution data
    if flux_df is not None and not flux_df.empty:
        for _, row in flux_df.iterrows():
            reaction_id = row['Reaction_ID']
            flux_value = row['Flux_Value']
            if abs(flux_value) > 0.001:  # Only include significant fluxes
                analysis_results['fba_analysis']['flux_distribution'][reaction_id] = flux_value
    
    # Add sensitivity analysis data
    if growth_rates:
        for i, rate in enumerate(GLUCOSE_RATES[:len(growth_rates)]):
            analysis_results['sensitivity_analysis']['glucose_sensitivity'][str(rate)] = growth_rates[i]
    
    if oxygen_growth_rates:
        for i, rate in enumerate(OXYGEN_RATES[:len(oxygen_growth_rates)]):
            analysis_results['sensitivity_analysis']['oxygen_sensitivity'][str(rate)] = oxygen_growth_rates[i]
    
    # Add pathway distribution data
    if flux_df is not None and not flux_df.empty:
        significant_fluxes = flux_df[abs(flux_df['Flux_Value']) > FLUX_THRESHOLD].copy()
        
        def categorize_reaction(reaction_id):
            if 'EX_' in reaction_id:
                return 'Exchange'
            elif 'BIOMASS' in reaction_id:
                return 'Biomass'
            elif any(x in reaction_id for x in ['ATPS', 'NADH', 'CYTBO']):
                return 'Energy'
            elif any(x in reaction_id for x in ['PYK', 'PGI', 'FBP', 'GAPD']):
                return 'Glycolysis'
            elif any(x in reaction_id for x in ['PDH', 'CS', 'AKGDH', 'SUCOAS']):
                return 'TCA_Cycle'
            else:
                return 'Other'
        
        significant_fluxes['Category'] = significant_fluxes['Reaction_ID'].apply(categorize_reaction)
        category_counts = significant_fluxes['Category'].value_counts()
        
        for category, count in category_counts.items():
            analysis_results['pathway_analysis']['pathway_distribution'][category] = int(count)
    
    # Save to JSON file
    json_file = os.path.join(OUTPUT_DIR, "analysis_results.json")
    with open(json_file, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    print(f"Analysis results saved to: {json_file}")

def main():
    """Main function to run the complete FBA analysis"""
    print("=" * 50)
    print(f"FBA Analysis - {MODEL_NAME}")
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
        
        # Step 4: Sensitivity analysis
        growth_rates, oxygen_growth_rates, anaerobic_growth = sensitivity_analysis(model)
        
        # Step 5: Gene knockout analysis
        knockout_results = gene_knockout_analysis(model)
        
        # Step 6: Create visualizations
        create_visualizations(growth_rates, oxygen_growth_rates, anaerobic_growth)
        
        # Step 7: Save analysis results to JSON
        save_analysis_results(model, solution, flux_df, growth_rates, oxygen_growth_rates, anaerobic_growth, knockout_results)
        
        print("\n" + "=" * 50)
        print("FBA Analysis Completed Successfully!")
        print(f"Results saved in: {OUTPUT_DIR}")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error during FBA analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
