# 3. [ ] Infer major metabolic pathways through functional annotations and metabolites

print("=== Infer Major Metabolic Pathways through Reaction Names and Metabolites ===\n")

# Define metabolic pathway keywords
pathway_keywords = {
    'Glycolysis': ['glucose', 'hexose', 'pfk', 'pgi', 'glyc', 'pyr', 'glc', 'g6p', 'f6p'],
    'TCA Cycle': ['citrate', 'succinate', 'fumarate', 'malate', 'oxaloacetate', 'isocitrate', 'succ', 'fum', 'mal', 'oaa', 'cit'],
    'Pentose Phosphate': ['6pgc', 'ru5p', 'x5p', 'r5p', 'g6pd', 'pentose', 'ribose'],
    'Amino Acid Metabolism': ['ala', 'gly', 'ser', 'thr', 'val', 'leu', 'ile', 'met', 'phe', 'tyr', 'trp', 'his', 'arg', 'lys', 'asp', 'glu', 'cys', 'asn', 'gln', 'pro'],
    'Nucleotide Metabolism': ['amp', 'gmp', 'cmp', 'ump', 'atp', 'gtp', 'ctp', 'utp', 'adp', 'gdp', 'cdp', 'udp', 'purine', 'pyrimidine'],
    'Lipid Metabolism': ['fatty', 'acyl', 'coa', 'lipid', 'phospholipid'],
    'Transport': ['transport', 'abc', 'pts', 'permease', 't2pp', 't3pp'],
    'Cofactor Metabolism': ['nad', 'fad', 'coa', 'folate', 'biotin', 'thiamine', 'riboflavin'],
    'Cell Wall': ['peptidoglycan', 'murein', 'lipopolysaccharide', 'lps'],
    'Energy Metabolism': ['respiratory', 'oxidative', 'phosphorylation', 'atp', 'nadh']
}

# Count reactions for each pathway
pathway_counts = defaultdict(int)

for rxn in model.reactions:
    rxn_name_lower = rxn.name.lower()
    rxn_id_lower = rxn.id.lower()
    
    # Get metabolites in reaction
    metabolites = [met.id.lower() for met in rxn.metabolites]
    all_text = rxn_name_lower + ' ' + rxn_id_lower + ' ' + ' '.join(metabolites)
    
    matched_pathways = []
    for pathway, keywords in pathway_keywords.items():
        if any(keyword in all_text for keyword in keywords):
            matched_pathways.append(pathway)
    
    if matched_pathways:
        for pathway in matched_pathways:
            pathway_counts[pathway] += 1
    else:
        pathway_counts['Other'] += 1

print("Inferred major metabolic pathway distribution:")
print("-" * 50)
total_reactions = sum(pathway_counts.values())
sorted_pathways = sorted(pathway_counts.items(), key=lambda x: x[1], reverse=True)

for pathway, count in sorted_pathways:
    percentage = (count / total_reactions) * 100
    print(f"{pathway:<25} {count:4d} reactions ({percentage:5.1f}%)")