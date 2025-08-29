print("=== Testing Different Environmental Conditions ===")

# Test different pH conditions by analyzing proton exchange
print("Testing pH sensitivity through proton exchange analysis...")

ph_conditions = {
    'Acidic (pH 5)': 10.0,    # Higher proton availability
    'Neutral (pH 7)': 0.0,   # Balanced
    'Basic (pH 9)': -10.0    # Lower proton availability  
}

print("pH Condition\tProton Exchange\tGrowth Rate\tStatus")
print("-" * 55)

for ph_name, h_bound in ph_conditions.items():
    test_model = model.copy()
    
    # Adjust proton exchange bounds
    if 'EX_h_e' in [r.id for r in test_model.reactions]:
        if h_bound > 0:  # Acidic - allow more proton uptake
            test_model.reactions.EX_h_e.lower_bound = -h_bound
        elif h_bound < 0:  # Basic - force proton secretion
            test_model.reactions.EX_h_e.upper_bound = -h_bound
            test_model.reactions.EX_h_e.lower_bound = -h_bound
    
    solution = test_model.optimize()
    growth_rate = solution.objective_value if solution.status == 'optimal' else 0.0
    
    print(f"{ph_name:<15}\t{h_bound:>8.1f}\t{growth_rate:>9.6f}\t{solution.status}")

# Test temperature stress through ATP maintenance requirements
print(f"\n=== Temperature Stress Simulation ===")
print("Simulating temperature effects through ATP maintenance...")

temp_conditions = {
    'Low (20°C)': 5.0,     # Lower maintenance
    'Optimal (37°C)': 8.39,  # Normal maintenance  
    'High (45°C)': 15.0    # Higher maintenance
}

print("Temperature\tATP Maintenance\tGrowth Rate\tStatus")
print("-" * 50)

for temp_name, atp_maintenance in temp_conditions.items():
    test_model = model.copy()
    
    # Find ATP maintenance reaction
    atp_maintenance_rxns = [r for r in test_model.reactions if 'maintenance' in r.id.lower() or r.id == 'ATPM']
    
    if atp_maintenance_rxns:
        atp_rxn = atp_maintenance_rxns[0]
        atp_rxn.lower_bound = atp_maintenance
        
        solution = test_model.optimize()
        growth_rate = solution.objective_value if solution.status == 'optimal' else 0.0
        
        print(f"{temp_name:<12}\t{atp_maintenance:>10.1f}\t{growth_rate:>9.6f}\t{solution.status}")
    else:
        print(f"{temp_name:<12}\tNo ATPM found\t0.000000\tN/A")

# Test osmotic stress through ion requirements
print(f"\n=== Osmotic Stress Analysis ===")
print("Testing osmotic conditions through ion exchange...")

osmotic_conditions = {
    'Low salt': {'EX_na1_e': -0.1, 'EX_k_e': -0.1},
    'Normal': {'EX_na1_e': -1.0, 'EX_k_e': -0.171184},  
    'High salt': {'EX_na1_e': -5.0, 'EX_k_e': -1.0}
}

print("Condition\tNa+ uptake\tK+ uptake\tGrowth Rate\tStatus")
print("-" * 55)

for condition_name, ion_bounds in osmotic_conditions.items():
    test_model = model.copy()
    
    # Set ion uptake bounds
    for ion_ex, bound in ion_bounds.items():
        if ion_ex in [r.id for r in test_model.reactions]:
            test_model.reactions.get_by_id(ion_ex).lower_bound = bound
    
    solution = test_model.optimize()
    growth_rate = solution.objective_value if solution.status == 'optimal' else 0.0
    
    na_bound = ion_bounds.get('EX_na1_e', 0.0)
    k_bound = ion_bounds.get('EX_k_e', 0.0) 
    
    print(f"{condition_name:<10}\t{na_bound:>7.1f}\t{k_bound:>7.3f}\t{growth_rate:>9.6f}\t{solution.status}")

print("\n✓ Step 6: Different environmental conditions testing completed")