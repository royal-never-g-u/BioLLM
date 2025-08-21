# 5. [ ] Create visualization charts to show metabolic network overview

print("=== Create Metabolic Network Visualization ===\n")

# Create output directory
import os
output_dir = '/tmp/agent_outputs/ee7af05a-15d4-4d75-bc6f-ae5ddae4ec6a'
os.makedirs(output_dir, exist_ok=True)

# 1. Metabolic pathway distribution pie chart
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Pie chart: metabolic pathway distribution
pathway_names = [name for name, count in sorted_pathways if count > 50]
pathway_values = [count for name, count in sorted_pathways if count > 50]
other_count = sum([count for name, count in sorted_pathways if count <= 50])

if other_count > 0:
    pathway_names.append('Other')
    pathway_values.append(other_count)

colors = plt.cm.Set3(np.linspace(0, 1, len(pathway_names)))
ax1.pie(pathway_values, labels=pathway_names, autopct='%1.1f%%', colors=colors, startangle=90)
ax1.set_title('iML1515 Metabolic Pathway Distribution', fontsize=14, fontweight='bold')

# Bar chart: main pathway reaction counts
ax2.bar(range(len(pathway_names)), pathway_values, color=colors)
ax2.set_xlabel('Metabolic Pathways')
ax2.set_ylabel('Reaction Count')
ax2.set_title('Main Metabolic Pathway Reaction Counts', fontsize=14, fontweight='bold')
ax2.set_xticks(range(len(pathway_names)))
ax2.set_xticklabels(pathway_names, rotation=45, ha='right')

# Basic statistics
stats = {
    'Reactions': len(model.reactions),
    'Metabolites': len(model.metabolites), 
    'Genes': len(model.genes),
    'Exchange Reactions': exchange_reactions,
    'Transport Reactions': transport_reactions
}

ax3.bar(stats.keys(), stats.values(), color='skyblue')
ax3.set_ylabel('Count')
ax3.set_title('iML1515 Model Basic Statistics', fontsize=14, fontweight='bold')
ax3.tick_params(axis='x', rotation=45)

# Reaction type distribution
reaction_types = {
    'Exchange Reactions': exchange_reactions,
    'Transport Reactions': transport_reactions,
    'Biomass Reactions': biomass_reactions,
    'Maintenance Reactions': maintenance_reactions,
    'Internal Reactions': len(model.reactions) - exchange_reactions - transport_reactions - biomass_reactions - maintenance_reactions
}

ax4.bar(reaction_types.keys(), reaction_types.values(), color='lightcoral')
ax4.set_ylabel('Reaction Count')
ax4.set_title('Reaction Type Distribution', fontsize=14, fontweight='bold')
ax4.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(f'{output_dir}/iML1515_metabolic_network_overview.png', dpi=300, bbox_inches='tight')
print(f"Metabolic network overview chart saved to: {output_dir}/iML1515_metabolic_network_overview.png")

# Generate detailed report
print(f"\n=== iML1515 Detailed Report ===")
print(f"Save path: {output_dir}/iML1515_analysis_report.txt")

with open(f'{output_dir}/iML1515_analysis_report.txt', 'w', encoding='utf-8') as f:
    f.write("iML1515 E. coli Metabolic Network Model Analysis Report\n")
    f.write("="*50 + "\n\n")
    
    f.write("Basic Information:\n")
    f.write(f"- Reaction count: {len(model.reactions)}\n")
    f.write(f"- Metabolite count: {len(model.metabolites)}\n") 
    f.write(f"- Gene count: {len(model.genes)}\n\n")
    
    f.write("Metabolic Pathway Distribution:\n")
    for pathway, count in sorted_pathways:
        percentage = (count / sum(pathway_counts.values())) * 100
        f.write(f"- {pathway}: {count} reactions ({percentage:.1f}%)\n")
    
    f.write(f"\nReaction Types:\n")
    f.write(f"- Exchange reactions: {exchange_reactions}\n")
    f.write(f"- Transport reactions: {transport_reactions}\n")
    f.write(f"- Biomass reactions: {biomass_reactions}\n")
    f.write(f"- Maintenance reactions: {maintenance_reactions}\n")

print("✓ Analysis completed!")