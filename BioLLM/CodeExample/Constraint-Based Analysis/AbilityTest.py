print("=== Analyzing Growth Predictions and Metabolic Capabilities ===")

# Test growth on different carbon sources
carbon_sources = {
    'glucose': 'EX_glc__D_e',
    'fructose': 'EX_fru_e', 
    'acetate': 'EX_ac_e',
    'succinate': 'EX_succ_e',
    'lactate': 'EX_lac__L_e',
    'glycerol': 'EX_glyc_e',
    'pyruvate': 'EX_pyr_e'
}

growth_results = {}

print("Testing growth on different carbon sources:")
print("Carbon Source\tGrowth Rate (h⁻¹)\tStatus")
print("-" * 45)

for carbon_name, exchange_id in carbon_sources.items():
    # Create a copy of the model for testing
    test_model = model.copy()
    
    # Close all carbon source uptakes first
    carbon_exchanges = ['EX_glc__D_e', 'EX_fru_e', 'EX_ac_e', 'EX_succ_e', 
                       'EX_lac__L_e', 'EX_glyc_e', 'EX_pyr_e']
    
    for ex in carbon_exchanges:
        if ex in [r.id for r in test_model.reactions]:
            test_model.reactions.get_by_id(ex).lower_bound = 0
    
    # Open the specific carbon source
    if exchange_id in [r.id for r in test_model.reactions]:
        test_model.reactions.get_by_id(exchange_id).lower_bound = -10.0
        
        # Optimize
        solution = test_model.optimize()
        growth_rate = solution.objective_value if solution.status == 'optimal' else 0.0
        growth_results[carbon_name] = growth_rate
        
        print(f"{carbon_name:<12}\t{growth_rate:.6f}\t\t{solution.status}")
    else:
        growth_results[carbon_name] = 0.0
        print(f"{carbon_name:<12}\t0.000000\t\tNot available")

# Test aerobic vs anaerobic conditions
print(f"\n=== Aerobic vs Anaerobic Growth Comparison ===")

# Aerobic conditions (already tested above with glucose)
aerobic_growth = 0.876997

# Anaerobic conditions
anaerobic_model = model.copy()
anaerobic_model.reactions.EX_o2_e.lower_bound = 0  # No oxygen uptake

anaerobic_solution = anaerobic_model.optimize()
anaerobic_growth = anaerobic_solution.objective_value if anaerobic_solution.status == 'optimal' else 0.0

print(f"Aerobic growth rate: {aerobic_growth:.6f} h⁻¹")
print(f"Anaerobic growth rate: {anaerobic_growth:.6f} h⁻¹")
print(f"Growth reduction: {((aerobic_growth - anaerobic_growth) / aerobic_growth * 100):.1f}%")

print("\n✓ Step 4: Growth predictions and metabolic capabilities analysis completed")