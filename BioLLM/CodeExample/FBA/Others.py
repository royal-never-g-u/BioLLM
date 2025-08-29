print("Step 5: Performing sensitivity analysis and constraint variations...")

# Test different glucose uptake rates
glucose_rates = [5, 10, 15, 20, 25]
growth_rates = []
flux_results = []

print("Testing different glucose uptake rates:")
print("Glucose Rate (mmol/gDW/h) | Growth Rate (h⁻¹)")
print("-" * 45)

for glucose_rate in glucose_rates:
    # Create a copy of the model
    test_model = model.copy()
    
    # Set glucose uptake rate
    test_model.reactions.EX_glc__D_e.lower_bound = -glucose_rate
    
    # Optimize
    solution = test_model.optimize()
    growth_rate = solution.objective_value if solution.status == 'optimal' else 0
    growth_rates.append(growth_rate)
    
    print(f"{glucose_rate:20.1f} | {growth_rate:.6f}")
    
    # Store detailed flux data for key reactions
    if solution.status == 'optimal':
        key_reactions = ['BIOMASS_Ec_iML1515_core_75p37M', 'EX_glc__D_e', 'EX_o2_e', 
                        'EX_co2_e', 'EX_h2o_e', 'ATPS4rpp', 'CYTBO3_4pp']
        flux_data = {'Glucose_Rate': glucose_rate, 'Growth_Rate': growth_rate}
        for rxn_id in key_reactions:
            flux_data[rxn_id] = solution.fluxes[rxn_id]
        flux_results.append(flux_data)

# Test different oxygen availability
print("\n\nTesting different oxygen availability:")
print("Oxygen Rate (mmol/gDW/h) | Growth Rate (h⁻¹)")
print("-" * 43)

oxygen_rates = [10, 20, 30, 40, 50]
oxygen_growth_rates = []

for oxygen_rate in oxygen_rates:
    test_model = model.copy()
    test_model.reactions.EX_glc__D_e.lower_bound = -10  # Reset glucose to default
    test_model.reactions.EX_o2_e.lower_bound = -oxygen_rate
    
    solution = test_model.optimize()
    growth_rate = solution.objective_value if solution.status == 'optimal' else 0
    oxygen_growth_rates.append(growth_rate)
    
    print(f"{oxygen_rate:19.1f} | {growth_rate:.6f}")

# Test anaerobic conditions
print("\n\nTesting anaerobic conditions:")
anaerobic_model = model.copy()
anaerobic_model.reactions.EX_glc__D_e.lower_bound = -10
anaerobic_model.reactions.EX_o2_e.lower_bound = 0  # No oxygen uptake

solution = anaerobic_model.optimize()
anaerobic_growth = solution.objective_value if solution.status == 'optimal' else 0
print(f"Anaerobic growth rate: {anaerobic_growth:.6f} h⁻¹")

# Test gene knockout effects
print("\n\nTesting single gene knockout effects on key genes:")
essential_test_genes = ['b0008', 'b0114', 'b1136', 'b2925', 'b0720']  # Sample genes
knockout_results = []

for gene_id in essential_test_genes:
    if gene_id in [g.id for g in model.genes]:
        test_model = model.copy()
        gene = test_model.genes.get_by_id(gene_id)
        
        # Perform knockout using cobra
        with test_model:
            gene.knock_out()
            solution = test_model.optimize()
            growth_rate = solution.objective_value if solution.status == 'optimal' else 0
            
        knockout_results.append({
            'Gene_ID': gene_id,
            'Growth_Rate': growth_rate,
            'Growth_Reduction': (0.876997 - growth_rate) / 0.876997 * 100
        })

if knockout_results:
    print("Gene ID | Growth Rate | Growth Reduction (%)")
    print("-" * 42)
    for result in knockout_results:
        print(f"{result['Gene_ID']:7s} | {result['Growth_Rate']:11.6f} | {result['Growth_Reduction']:15.2f}")

# Save sensitivity analysis results
sensitivity_df = pd.DataFrame({
    'Glucose_Rate': glucose_rates,
    'Growth_Rate': growth_rates
})

sensitivity_file = os.path.join(output_dir, "sensitivity_analysis.csv")
sensitivity_df.to_csv(sensitivity_file, index=False)
print(f"\nSensitivity analysis saved to: {sensitivity_file}")

flux_results_df = pd.DataFrame(flux_results)
flux_results_file = os.path.join(output_dir, "detailed_flux_results.csv")
flux_results_df.to_csv(flux_results_file, index=False)
print(f"Detailed flux results saved to: {flux_results_file}")