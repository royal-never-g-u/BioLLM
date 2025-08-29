print("=== Performing Sensitivity Analysis and Robustness Testing ===")

# Flux Variability Analysis (FVA) for key reactions
print("Performing Flux Variability Analysis (FVA)...")

# Get a representative set of reactions for FVA
key_reactions = ['BIOMASS_Ec_iML1515_core_75p37M', 'EX_glc__D_e', 'EX_o2_e', 
                'ATPS4rpp', 'PGK', 'PYK', 'CS', 'ACALD']

# Filter to only include reactions that exist in the model
existing_reactions = [rxn_id for rxn_id in key_reactions if rxn_id in [r.id for r in model.reactions]]

if existing_reactions:
    fva_result = cobra.flux_analysis.flux_variability_analysis(model, existing_reactions)
    
    print("\nFlux Variability Analysis Results:")
    print("Reaction ID\t\tMinimum\t\tMaximum\t\tRange")
    print("-" * 60)
    
    for rxn_id in existing_reactions:
        min_flux = fva_result.loc[rxn_id, 'minimum']
        max_flux = fva_result.loc[rxn_id, 'maximum']
        flux_range = max_flux - min_flux
        print(f"{rxn_id:<20}\t{min_flux:.6f}\t{max_flux:.6f}\t{flux_range:.6f}")

# Essential genes analysis
print(f"\n=== Essential Genes Analysis ===")
print("Performing single gene deletion analysis...")

# Perform gene essentiality analysis on a subset due to computational time
essential_genes = []
sample_genes = list(model.genes)[:50]  # Test first 50 genes as sample

print(f"Testing {len(sample_genes)} genes for essentiality...")

for gene in sample_genes:
    # Perform single gene knockout
    with model:  # Use context manager to automatically revert changes
        gene.knock_out()
        solution = model.optimize()
        
        # Consider a gene essential if growth drops below 1% of wild-type
        if solution.status == 'optimal':
            growth_ratio = solution.objective_value / aerobic_growth
            if growth_ratio < 0.01:  # Less than 1% of wild-type growth
                essential_genes.append(gene.id)

print(f"Found {len(essential_genes)} essential genes out of {len(sample_genes)} tested:")
for gene_id in essential_genes[:10]:  # Show first 10
    print(f"  {gene_id}")

if len(essential_genes) > 10:
    print(f"  ... and {len(essential_genes) - 10} more")

# Robustness analysis - test growth under nutrient limitations
print(f"\n=== Nutrient Limitation Robustness Analysis ===")

nutrients_to_test = {
    'Glucose': 'EX_glc__D_e',
    'Oxygen': 'EX_o2_e', 
    'Phosphate': 'EX_pi_e',
    'Nitrogen': 'EX_nh4_e'
}

print("Nutrient\t\tUptake Rate\tGrowth Rate\tGrowth Efficiency")
print("-" * 65)

for nutrient_name, exchange_id in nutrients_to_test.items():
    if exchange_id in [r.id for r in model.reactions]:
        test_model = model.copy()
        
        # Test at 50% of normal uptake rate
        original_bound = test_model.reactions.get_by_id(exchange_id).lower_bound
        limited_bound = original_bound * 0.5
        
        test_model.reactions.get_by_id(exchange_id).lower_bound = limited_bound
        solution = test_model.optimize()
        
        growth_rate = solution.objective_value if solution.status == 'optimal' else 0.0
        efficiency = growth_rate / aerobic_growth if aerobic_growth > 0 else 0.0
        
        print(f"{nutrient_name:<15}\t{limited_bound:.6f}\t{growth_rate:.6f}\t{efficiency:.3f}")

print("\n✓ Step 5: Sensitivity analysis and robustness testing completed")