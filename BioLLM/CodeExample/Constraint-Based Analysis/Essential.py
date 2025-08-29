print("=== Essential Reactions Analysis ===")

# Perform reaction essentiality analysis on key metabolic pathways
print("Analyzing reaction essentiality in central metabolism...")

# Key reactions from central metabolism
central_reactions = [
    'PGI',     # Glucose-6-phosphate isomerase
    'PFK',     # Phosphofructokinase  
    'FBA',     # Fructose-bisphosphate aldolase
    'TPI',     # Triose phosphate isomerase
    'GAPD',    # Glyceraldehyde-3-phosphate dehydrogenase
    'PGK',     # Phosphoglycerate kinase
    'PGM',     # Phosphoglycerate mutase
    'ENO',     # Enolase
    'PYK',     # Pyruvate kinase
    'CS',      # Citrate synthase
    'ACONT',   # Aconitate hydratase
    'ICDHyr',  # Isocitrate dehydrogenase
    'AKGDH',   # α-ketoglutarate dehydrogenase
    'SUCOAS',  # Succinate-CoA synthetase
    'SUCDi',   # Succinate dehydrogenase
    'FUM',     # Fumarase
    'MDH'      # Malate dehydrogenase
]

# Filter to existing reactions
existing_central_rxns = [rxn_id for rxn_id in central_reactions if rxn_id in [r.id for r in model.reactions]]

essential_reactions = []
print(f"\nTesting {len(existing_central_rxns)} central metabolism reactions for essentiality...")

print("Reaction\tWild-type flux\tKnockout growth\tEssential?")
print("-" * 60)

# Get wild-type fluxes first
wt_solution = model.optimize()
wt_growth = wt_solution.objective_value

for rxn_id in existing_central_rxns:
    # Get wild-type flux
    wt_flux = wt_solution.fluxes[rxn_id] if wt_solution.status == 'optimal' else 0.0
    
    # Test reaction knockout
    with model:
        rxn = model.reactions.get_by_id(rxn_id)
        rxn.knock_out()
        
        ko_solution = model.optimize()
        ko_growth = ko_solution.objective_value if ko_solution.status == 'optimal' else 0.0
        
        # Consider essential if growth drops below 1% of wild-type
        is_essential = (ko_growth / wt_growth) < 0.01 if wt_growth > 0 else ko_growth == 0
        
        if is_essential:
            essential_reactions.append(rxn_id)
        
        print(f"{rxn_id:<12}\t{wt_flux:>10.6f}\t{ko_growth:>12.6f}\t{'Yes' if is_essential else 'No'}")

print(f"\nFound {len(essential_reactions)} essential reactions in central metabolism:")
for rxn_id in essential_reactions:
    reaction = model.reactions.get_by_id(rxn_id)
    print(f"  {rxn_id}: {reaction.name}")

print("\n✓ Step 7: Essential genes and reactions analysis completed")