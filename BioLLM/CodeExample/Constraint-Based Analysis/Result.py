print("=== Creating Visualizations and Final Report ===")

# Create comprehensive visualizations
plt.style.use('default')
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('iML1515 E. coli Metabolic Model: Constraint-Based Analysis Results', fontsize=16, fontweight='bold')

# Plot 1: Growth rates on different carbon sources
ax1 = axes[0, 0]
carbon_names = list(growth_results.keys())
growth_rates = list(growth_results.values())

bars1 = ax1.bar(carbon_names, growth_rates, color='steelblue', alpha=0.7)
ax1.set_title('Growth Rates on Different Carbon Sources', fontweight='bold')
ax1.set_ylabel('Growth Rate (h⁻¹)')
ax1.set_xlabel('Carbon Source')
ax1.tick_params(axis='x', rotation=45)

# Add value labels on bars
for bar, rate in zip(bars1, growth_rates):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{rate:.3f}', ha='center', va='bottom', fontsize=9)

# Plot 2: Aerobic vs Anaerobic growth
ax2 = axes[0, 1]
conditions = ['Aerobic', 'Anaerobic']
growth_vals = [aerobic_growth, anaerobic_growth]
colors = ['red', 'blue']

bars2 = ax2.bar(conditions, growth_vals, color=colors, alpha=0.7)
ax2.set_title('Aerobic vs Anaerobic Growth', fontweight='bold')
ax2.set_ylabel('Growth Rate (h⁻¹)')

# Add value labels
for bar, val in zip(bars2, growth_vals):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{val:.3f}', ha='center', va='bottom', fontsize=10)

# Plot 3: Temperature sensitivity
ax3 = axes[1, 0]
temp_names = ['20°C', '37°C', '45°C']
temp_growth = [0.883994, 0.871242, 0.846377]  # From temperature analysis

bars3 = ax3.bar(temp_names, temp_growth, color='orange', alpha=0.7)
ax3.set_title('Temperature Effects on Growth', fontweight='bold')
ax3.set_ylabel('Growth Rate (h⁻¹)')
ax3.set_xlabel('Temperature')

# Add value labels
for bar, val in zip(bars3, temp_growth):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{val:.3f}', ha='center', va='bottom', fontsize=10)

# Plot 4: Osmotic stress effects
ax4 = axes[1, 1]
osmotic_names = ['Low salt', 'Normal', 'High salt']
osmotic_growth = [0.512313, 0.876997, 0.876997]  # From osmotic analysis

bars4 = ax4.bar(osmotic_names, osmotic_growth, color='green', alpha=0.7)
ax4.set_title('Osmotic Stress Effects', fontweight='bold')
ax4.set_ylabel('Growth Rate (h⁻¹)')
ax4.set_xlabel('Salt Concentration')

# Add value labels
for bar, val in zip(bars4, osmotic_growth):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
             f'{val:.3f}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()

# Save the figure
fig_path = os.path.join(output_dir, 'iML1515_constraint_based_analysis.png')
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"Visualization saved to: {fig_path}")

# Update final plan status
print("\n=== Final Plan Status ===")
print("1. [✓] Search for and obtain the iML1515 model file")
print("2. [✓] Load and examine the model structure and properties") 
print("3. [✓] Perform basic Flux Balance Analysis (FBA)")
print("4. [✓] Analyze growth predictions and metabolic capabilities")
print("5. [✓] Perform sensitivity analysis and robustness testing")
print("6. [✓] Test different environmental conditions")
print("7. [✓] Analyze essential genes and reactions")
print("8. [✓] Generate comprehensive experimental report with conclusions")

print("\n✓ Step 8: Visualizations created and analysis completed")