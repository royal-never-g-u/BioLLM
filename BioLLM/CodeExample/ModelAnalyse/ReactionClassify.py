# It seems the subsystem attribute might be empty, let's check other ways to get pathway information
print("=== Check Reaction Annotations and Classification ===\n")

# Check detailed information of several sample reactions
print("Detailed information of first 10 reactions:")
for i, rxn in enumerate(model.reactions[:10]):
    print(f"{i+1}. ID: {rxn.id}")
    print(f"   Name: {rxn.name}")
    print(f"   Subsystem: {rxn.subsystem}")
    print(f"   Gene rule: {rxn.gene_reaction_rule}")
    print(f"   Reaction: {rxn.reaction}")
    print()

print("\n=== Classification by Reaction ID Pattern ===")

# Infer functional classification through reaction ID prefixes
reaction_prefixes = defaultdict(int)
exchange_reactions = 0
transport_reactions = 0
biomass_reactions = 0
maintenance_reactions = 0

for rxn in model.reactions:
    rxn_id = rxn.id
    
    if rxn_id.startswith('EX_'):
        exchange_reactions += 1
    elif 'biomass' in rxn_id.lower():
        biomass_reactions += 1
    elif 'atpm' in rxn_id.lower() or 'maintenance' in rxn_id.lower():
        maintenance_reactions += 1
    elif any(word in rxn_id.lower() for word in ['transport', 'abc', 'pts']):
        transport_reactions += 1
    
    # Get prefix
    if '_' in rxn_id:
        prefix = rxn_id.split('_')[0]
        reaction_prefixes[prefix] += 1

print(f"Exchange reactions (EX_): {exchange_reactions}")
print(f"Biomass reactions: {biomass_reactions}")
print(f"Maintenance reactions: {maintenance_reactions}")
print(f"Transport-related reactions: {transport_reactions}")

print(f"\nMain reaction prefixes:")
sorted_prefixes = sorted(reaction_prefixes.items(), key=lambda x: x[1], reverse=True)
for prefix, count in sorted_prefixes[:15]:
    print(f"{prefix}: {count}")