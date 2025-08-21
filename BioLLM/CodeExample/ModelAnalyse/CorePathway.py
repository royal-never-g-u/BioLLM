# 4. [ ] Detailed analysis of specific reactions in core metabolic pathways

print("=== Detailed Analysis of Core Metabolic Pathways ===\n")

# Analyze key reactions in glycolysis pathway
print("1. Key reactions in glycolysis pathway:")
print("-" * 40)
glycolysis_reactions = []
for rxn in model.reactions:
    if any(keyword in rxn.id.lower() or keyword in rxn.name.lower() 
           for keyword in ['pgi', 'pfk', 'fba', 'tpi', 'gapdh', 'pgk', 'pgm', 'eno', 'pyk']):
        glycolysis_reactions.append(rxn)

for rxn in glycolysis_reactions[:10]:  # Show first 10
    print(f"ID: {rxn.id:10} | {rxn.name}")

print(f"\n2. TCA cycle key reactions:")
print("-" * 40)
tca_reactions = []
for rxn in model.reactions:
    if any(keyword in rxn.id.lower() or keyword in rxn.name.lower()
           for keyword in ['cs', 'idh', 'akgdh', 'sucoas', 'sdh', 'fum', 'mdh']):
        tca_reactions.append(rxn)

for rxn in tca_reactions[:10]:
    print(f"ID: {rxn.id:10} | {rxn.name}")

print(f"\n3. Exchange reactions (nutrients and products):")
print("-" * 40)
exchange_rxns = [rxn for rxn in model.reactions if rxn.id.startswith('EX_')]
important_exchanges = []
for rxn in exchange_rxns:
    if any(nutrient in rxn.id.lower() for nutrient in ['glc', 'o2', 'pi', 'so4', 'nh4', 'co2', 'h2o']):
        important_exchanges.append(rxn)

for rxn in important_exchanges[:15]:
    print(f"ID: {rxn.id:15} | {rxn.name}")