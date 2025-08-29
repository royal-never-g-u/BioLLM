# Updated plan progress
print("Plan Progress:")
print("1. [✓] Search for and obtain the iML1515 model file")
print("2. [✓] Load and examine the model structure and properties")
print("3. [ ] Perform basic Flux Balance Analysis (FBA)")
print("4. [ ] Analyze growth predictions and metabolic capabilities")
print("5. [ ] Perform sensitivity analysis and robustness testing")
print("6. [ ] Test different environmental conditions")
print("7. [ ] Analyze essential genes and reactions")
print("8. [ ] Generate comprehensive experimental report with conclusions")

print("\n=== Performing Basic Flux Balance Analysis ===")

# Perform FBA on the default medium
solution = model.optimize()

print(f"FBA Solution Status: {solution.status}")
print(f"Objective Value (Growth Rate): {solution.objective_value:.6f} h⁻¹")

if solution.status == 'optimal':
    print(f"Model is feasible and optimal solution found")
    
    # Get flux distribution for exchange reactions
    exchange_fluxes = {}
    for reaction in exchange_reactions:
        flux = solution.fluxes[reaction.id]
        if abs(flux) > 1e-6:  # Only show non-zero fluxes
            exchange_fluxes[reaction.id] = flux
    
    print(f"\nActive exchange reactions ({len(exchange_fluxes)} out of {len(exchange_reactions)}):")
    
    # Sort by flux magnitude
    sorted_fluxes = sorted(exchange_fluxes.items(), key=lambda x: abs(x[1]), reverse=True)
    
    print("Top 10 uptake reactions (negative flux):")
    uptake_count = 0
    for rxn_id, flux in sorted_fluxes:
        if flux < -1e-6 and uptake_count < 10:
            rxn = model.reactions.get_by_id(rxn_id)
            metabolite_name = rxn.metabolites
            print(f"  {rxn_id}: {flux:.6f} mmol/gDW/h")
            uptake_count += 1
    
    print("\nTop 10 secretion reactions (positive flux):")
    secretion_count = 0
    for rxn_id, flux in sorted_fluxes:
        if flux > 1e-6 and secretion_count < 10:
            rxn = model.reactions.get_by_id(rxn_id)
            print(f"  {rxn_id}: {flux:.6f} mmol/gDW/h")
            secretion_count += 1

else:
    print(f"Model optimization failed with status: {solution.status}")

print("\n✓ Step 3: Basic FBA completed")