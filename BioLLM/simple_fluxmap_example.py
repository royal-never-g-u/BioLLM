#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Metabolic Fluxmap Example

This script demonstrates how to create a simple fluxmap visualization
for a metabolic network using COBRA library.

Key Features:
1. Load .mat file using cobra
2. Perform FBA to get flux values
3. Create network visualization with flux-weighted nodes and edges
4. Color-code pathways and size-code flux values

Usage:
python simple_fluxmap_example.py
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import cobra
import warnings
warnings.filterwarnings('ignore')

def load_model_and_analyze(model_path):
    """
    Load metabolic model and perform FBA analysis
    
    Args:
        model_path: Path to the .mat file
        
    Returns:
        tuple: (model, solution, flux_data)
    """
    print("Loading metabolic model...")
    
    # Load model from .mat file
    model = cobra.io.load_matlab_model(model_path)
    print(f"✓ Model loaded: {model.id}")
    print(f"  - Reactions: {len(model.reactions)}")
    print(f"  - Metabolites: {len(model.metabolites)}")
    
    # Perform FBA
    print("Performing FBA analysis...")
    solution = model.optimize()
    
    if solution.status == 'optimal':
        print(f"✓ FBA successful! Growth rate: {solution.objective_value:.6f} h⁻¹")
        
        # Create flux data
        flux_data = pd.DataFrame({
            'Reaction_ID': [rxn.id for rxn in model.reactions],
            'Reaction_Name': [rxn.name for rxn in model.reactions],
            'Flux_Value': [solution.fluxes[rxn.id] for rxn in model.reactions],
            'Abs_Flux': [abs(solution.fluxes[rxn.id]) for rxn in model.reactions]
        })
        
        return model, solution, flux_data
    else:
        print(f"✗ FBA failed: {solution.status}")
        return None, None, None

def classify_pathway(reaction_id):
    """Classify reaction into metabolic pathway"""
    rxn_id_lower = reaction_id.lower()
    
    pathway_keywords = {
        'Glycolysis': ['pgi', 'pfk', 'fba', 'tpi', 'gapdh', 'pgk', 'pgm', 'eno', 'pyk'],
        'TCA Cycle': ['cs', 'idh', 'akgdh', 'sucoas', 'sdh', 'fum', 'mdh'],
        'Pentose Phosphate': ['6pgc', 'ru5p', 'x5p', 'r5p', 'g6pd'],
        'Amino Acid Metabolism': ['ala', 'gly', 'ser', 'thr', 'val', 'leu', 'ile'],
        'Transport': ['transport', 'abc', 'pts', 'permease'],
        'Exchange': ['ex_'],
        'Biomass': ['biomass']
    }
    
    for pathway, keywords in pathway_keywords.items():
        if any(keyword in rxn_id_lower for keyword in keywords):
            return pathway
    
    return 'Other'

def create_fluxmap_visualization(model, flux_data, output_file="fluxmap.png"):
    """
    Create fluxmap visualization
    
    Args:
        model: COBRA model object
        flux_data: DataFrame with flux values
        output_file: Output file path
    """
    print("Creating fluxmap visualization...")
    
    # Add pathway classification
    flux_data['Pathway'] = flux_data['Reaction_ID'].apply(classify_pathway)
    
    # Get top reactions by flux
    top_reactions = flux_data.nlargest(30, 'Abs_Flux')
    
    # Create network graph
    G = nx.DiGraph()
    
    # Add nodes (reactions)
    for _, row in top_reactions.iterrows():
        G.add_node(row['Reaction_ID'], 
                  name=row['Reaction_Name'],
                  flux=row['Flux_Value'],
                  pathway=row['Pathway'])
    
    # Add edges based on metabolite connections
    for _, row in top_reactions.iterrows():
        rxn = model.reactions.get_by_id(row['Reaction_ID'])
        
        # Find connected reactions through shared metabolites
        for met in rxn.metabolites:
            for connected_rxn in met.reactions:
                if connected_rxn.id in top_reactions['Reaction_ID'].values:
                    if row['Reaction_ID'] != connected_rxn.id:
                        G.add_edge(row['Reaction_ID'], connected_rxn.id)
    
    # Create visualization
    plt.figure(figsize=(14, 10))
    
    # Position nodes
    pos = nx.spring_layout(G, k=2, iterations=30)
    
    # Define colors for pathways
    pathway_colors = {
        'Glycolysis': '#FF6B6B',
        'TCA Cycle': '#4ECDC4', 
        'Pentose Phosphate': '#45B7D1',
        'Amino Acid Metabolism': '#96CEB4',
        'Transport': '#DDA0DD',
        'Exchange': '#98D8C8',
        'Biomass': '#F7DC6F',
        'Other': '#BDC3C7'
    }
    
    # Draw nodes with flux-weighted sizes
    node_colors = [pathway_colors.get(G.nodes[node]['pathway'], '#BDC3C7') 
                  for node in G.nodes()]
    node_sizes = [abs(G.nodes[node]['flux']) * 800 for node in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, 
                          node_color=node_colors,
                          node_size=node_sizes,
                          alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, 
                          edge_color='gray',
                          alpha=0.4,
                          arrows=True,
                          arrowsize=8)
    
    # Add labels for important nodes
    important_nodes = [node for node in G.nodes() 
                      if abs(G.nodes[node]['flux']) > np.percentile([abs(G.nodes[n]['flux']) for n in G.nodes()], 80)]
    
    labels = {node: node for node in important_nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=7, font_weight='bold')
    
    # Create legend
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                 markerfacecolor=color, markersize=8, label=pathway)
                      for pathway, color in pathway_colors.items()]
    
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
    plt.title('Metabolic Network Fluxmap\n(Node size = Flux magnitude, Color = Pathway)', 
             fontsize=14, fontweight='bold')
    plt.axis('off')
    
    # Save plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Fluxmap saved to: {output_file}")
    plt.close()

def create_flux_heatmap(flux_data, output_file="flux_heatmap.png"):
    """
    Create heatmap of flux values
    
    Args:
        flux_data: DataFrame with flux values
        output_file: Output file path
    """
    print("Creating flux heatmap...")
    
    # Get top reactions
    top_reactions = flux_data.nlargest(20, 'Abs_Flux')
    
    # Create heatmap data
    heatmap_data = top_reactions[['Reaction_ID', 'Flux_Value']].set_index('Reaction_ID').T
    
    # Create heatmap
    plt.figure(figsize=(12, 4))
    
    import seaborn as sns
    sns.heatmap(heatmap_data, annot=True, cmap='RdBu_r', center=0, 
               fmt='.3f', cbar_kws={'label': 'Flux Value'})
    
    plt.title('Top 20 Reactions by Flux Magnitude', fontsize=14, fontweight='bold')
    plt.xlabel('Reactions')
    plt.ylabel('Flux')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Heatmap saved to: {output_file}")
    plt.close()

def main():
    """Main function"""
    
    # Model file path - update this to your .mat file
    model_path = "downloads/e_coli_core.mat"
    
    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        print("Please update the model_path variable to point to your .mat file")
        return
    
    # Load model and perform analysis
    model, solution, flux_data = load_model_and_analyze(model_path)
    
    if model is None:
        print("Failed to load model or perform FBA")
        return
    
    # Create visualizations
    create_fluxmap_visualization(model, flux_data, "metabolic_fluxmap.png")
    create_flux_heatmap(flux_data, "flux_heatmap.png")
    
    # Print summary
    print("\n" + "="*50)
    print("FLUXMAP GENERATION COMPLETED")
    print("="*50)
    print(f"Generated files:")
    print("  - metabolic_fluxmap.png (Network visualization)")
    print("  - flux_heatmap.png (Heatmap visualization)")
    print("\nKey features:")
    print("  - Node size represents flux magnitude")
    print("  - Node color represents metabolic pathway")
    print("  - Edges show metabolite connections")
    print("  - Positive fluxes: forward direction")
    print("  - Negative fluxes: reverse direction")

if __name__ == "__main__":
    main()
