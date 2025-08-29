print("Step 3: Performing basic FBA analysis...")

# Perform FBA with default settings
solution = model.optimize()
print(f"FBA Solution Status: {solution.status}")
print(f"Objective Value (Growth Rate): {solution.objective_value:.6f} h⁻¹")

if solution.status == 'optimal':
    print("\nFBA analysis successful!")
    
    # Get biomass reaction details
    biomass_reaction = model.reactions.get_by_id("BIOMASS_Ec_iML1515_core_75p37M")
    print(f"\nBiomass reaction: {biomass_reaction.id}")
    print(f"Biomass equation: {biomass_reaction.reaction}")
    
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
    flux_file = os.path.join(output_dir, "flux_distribution.csv")
    flux_df.to_csv(flux_file, index=False)
    print(f"Flux distribution saved to: {flux_file}")
    
    # Show top 10 reactions with highest absolute flux
    top_fluxes = flux_df[flux_df['Flux_Value'] != 0].copy()
    top_fluxes['Abs_Flux'] = abs(top_fluxes['Flux_Value'])
    top_fluxes = top_fluxes.nlargest(10, 'Abs_Flux')
    
    print(f"\nTop 10 reactions with highest flux:")
    print(top_fluxes[['Reaction_ID', 'Reaction_Name', 'Flux_Value']].to_string(index=False))
    
else:
    print(f"FBA failed with status: {solution.status}")