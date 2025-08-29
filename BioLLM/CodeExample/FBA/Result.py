print("Step 6: Generating visualizations...")

# Set up the plotting style
plt.style.use('seaborn-v0_8')
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
fig.suptitle('iML1515 E. coli Metabolic Model - Flux Balance Analysis Results', fontsize=16, fontweight='bold')

# 1. Growth rate vs glucose uptake rate
axes[0,0].plot(glucose_rates, growth_rates, 'o-', linewidth=2, markersize=8, color='navy')
axes[0,0].set_xlabel('Glucose Uptake Rate (mmol/gDW/h)')
axes[0,0].set_ylabel('Growth Rate (h⁻¹)')
axes[0,0].set_title('A. Growth Rate vs Glucose Uptake')
axes[0,0].grid(True, alpha=0.3)

# 2. Growth rate vs oxygen availability
axes[0,1].plot(oxygen_rates, oxygen_growth_rates, 's-', linewidth=2, markersize=8, color='darkred')
axes[0,1].set_xlabel('Oxygen Availability (mmol/gDW/h)')
axes[0,1].set_ylabel('Growth Rate (h⁻¹)')
axes[0,1].set_title('B. Growth Rate vs Oxygen Availability')
axes[0,1].grid(True, alpha=0.3)

# 3. Flux distribution by pathway category
pathway_data = pd.read_csv(os.path.join(output_dir, "pathway_analysis.csv"))
category_counts = pathway_data['Category'].value_counts()

colors = plt.cm.Set3(np.linspace(0, 1, len(category_counts)))
axes[0,2].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%', 
              colors=colors, startangle=90)
axes[0,2].set_title('C. Active Reactions by Pathway Category')

# 4. Top flux values (bar plot)
top_fluxes = pathway_data.nlargest(15, 'Abs_Flux')
y_pos = range(len(top_fluxes))
axes[1,0].barh(y_pos, top_fluxes['Flux_Value'], color='steelblue')
axes[1,0].set_yticks(y_pos)
axes[1,0].set_yticklabels(top_fluxes['Reaction_ID'], fontsize=8)
axes[1,0].set_xlabel('Flux Value (mmol/gDW/h)')
axes[1,0].set_title('D. Top 15 Reaction Fluxes')
axes[1,0].grid(True, alpha=0.3, axis='x')

# 5. Exchange reactions (uptake vs secretion)
exchange_data = pathway_data[pathway_data['Category'] == 'Exchange'].copy()
uptake = exchange_data[exchange_data['Flux_Value'] < 0]['Flux_Value'].abs()
secretion = exchange_data[exchange_data['Flux_Value'] > 0]['Flux_Value']

categories = ['Uptake', 'Secretion']
values = [uptake.sum(), secretion.sum()]
axes[1,1].bar(categories, values, color=['lightcoral', 'lightblue'])
axes[1,1].set_ylabel('Total Flux (mmol/gDW/h)')
axes[1,1].set_title('E. Total Uptake vs Secretion Fluxes')

# 6. Metabolic efficiency comparison
conditions = ['Aerobic\n(Standard)', 'Aerobic\n(Low O₂)', 'Anaerobic']
growth_values = [0.876997, 0.531524, 0.157540]
colors_bar = ['green', 'orange', 'red']

bars = axes[1,2].bar(conditions, growth_values, color=colors_bar, alpha=0.7)
axes[1,2].set_ylabel('Growth Rate (h⁻¹)')
axes[1,2].set_title('F. Growth Rate Under Different Conditions')
axes[1,2].set_ylim(0, 1.0)

# Add value labels on bars
for bar, value in zip(bars, growth_values):
    axes[1,2].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                   f'{value:.3f}', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plot_file = os.path.join(output_dir, "fba_analysis_results.png")
plt.savefig(plot_file, dpi=300, bbox_inches='tight')
print(f"Comprehensive analysis plot saved to: {plot_file}")

# Generate pathway flux heatmap
print("\nGenerating pathway flux heatmap...")
plt.figure(figsize=(12, 8))

# Get flux data for different glucose concentrations
flux_results_df = pd.read_csv(os.path.join(output_dir, "detailed_flux_results.csv"))

# Prepare data for heatmap
heatmap_data = flux_results_df.set_index('Glucose_Rate')
heatmap_data = heatmap_data.drop('Growth_Rate', axis=1)

# Normalize fluxes for better visualization
heatmap_data_norm = heatmap_data.div(heatmap_data.abs().max(), axis=1)

sns.heatmap(heatmap_data_norm.T, annot=True, cmap='RdBu_r', center=0, 
            fmt='.2f', cbar_kws={'label': 'Normalized Flux'})
plt.title('Key Reaction Fluxes vs Glucose Uptake Rate', fontsize=14, fontweight='bold')
plt.xlabel('Glucose Uptake Rate (mmol/gDW/h)')
plt.ylabel('Reactions')
plt.tight_layout()

heatmap_file = os.path.join(output_dir, "pathway_flux_heatmap.png")
plt.savefig(heatmap_file, dpi=300, bbox_inches='tight')
print(f"Pathway flux heatmap saved to: {heatmap_file}")

plt.show()