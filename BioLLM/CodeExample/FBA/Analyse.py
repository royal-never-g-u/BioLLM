print("Step 4: Analyzing flux distributions and key pathways...")

# Load the flux distribution
flux_df = pd.read_csv(os.path.join(output_dir, "flux_distribution.csv"))

# Filter for reactions with significant flux (>0.001 absolute value)
significant_fluxes = flux_df[abs(flux_df['Flux_Value']) > 0.001].copy()
significant_fluxes['Abs_Flux'] = abs(significant_fluxes['Flux_Value'])

print(f"Number of reactions with significant flux (>0.001): {len(significant_fluxes)}")

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
pathway_file = os.path.join(output_dir, "pathway_analysis.csv")
significant_fluxes.to_csv(pathway_file, index=False)
print(f"\nPathway analysis saved to: {pathway_file}")