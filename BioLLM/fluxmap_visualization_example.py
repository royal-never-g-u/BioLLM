#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metabolic Pathway Fluxmap Visualization Example

This script demonstrates how to create fluxmap visualizations for metabolic networks
using COBRA library. It shows different approaches to visualize flux distributions
on metabolic pathway maps.

Features:
1. Load metabolic model from .mat file
2. Perform FBA analysis to get flux values
3. Create various fluxmap visualizations:
   - Network graph with flux-weighted edges
   - Heatmap of pathway fluxes
   - Sankey diagram of major pathways
   - Interactive flux distribution plots

Author: BioLLM Team
Date: 2024
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import cobra
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
plt.style.use('default')
sns.set_palette("husl")

class MetabolicFluxmapVisualizer:
    """
    Class for creating fluxmap visualizations of metabolic networks
    """
    
    def __init__(self, model_path, output_dir="fluxmap_results"):
        """
        Initialize the visualizer
        
        Args:
            model_path: Path to the metabolic model file (.mat, .xml, .json)
            output_dir: Directory to save visualization results
        """
        self.model_path = model_path
        self.output_dir = output_dir
        self.model = None
        self.solution = None
        self.flux_data = None
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
    def load_model(self):
        """Load the metabolic model"""
        print("Loading metabolic model...")
        
        try:
            # Try different loading methods based on file extension
            if self.model_path.endswith('.mat'):
                self.model = cobra.io.load_matlab_model(self.model_path)
            elif self.model_path.endswith('.xml') or self.model_path.endswith('.sbml'):
                self.model = cobra.io.read_sbml_model(self.model_path)
            elif self.model_path.endswith('.json'):
                self.model = cobra.io.load_json_model(self.model_path)
            else:
                # Try generic loading
                self.model = cobra.io.load_model(self.model_path)
                
            print(f"✓ Model loaded successfully!")
            print(f"  - Model ID: {self.model.id}")
            print(f"  - Reactions: {len(self.model.reactions)}")
            print(f"  - Metabolites: {len(self.model.metabolites)}")
            print(f"  - Genes: {len(self.model.genes)}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            return False
    
    def perform_fba(self):
        """Perform Flux Balance Analysis"""
        print("Performing FBA analysis...")
        
        try:
            self.solution = self.model.optimize()
            
            if self.solution.status == 'optimal':
                print(f"✓ FBA completed successfully!")
                print(f"  - Growth rate: {self.solution.objective_value:.6f} h⁻¹")
                print(f"  - Status: {self.solution.status}")
                
                # Create flux data DataFrame
                self.flux_data = pd.DataFrame({
                    'Reaction_ID': [rxn.id for rxn in self.model.reactions],
                    'Reaction_Name': [rxn.name for rxn in self.model.reactions],
                    'Flux_Value': [self.solution.fluxes[rxn.id] for rxn in self.model.reactions],
                    'Abs_Flux': [abs(self.solution.fluxes[rxn.id]) for rxn in self.model.reactions],
                    'Reaction_Formula': [rxn.reaction for rxn in self.model.reactions]
                })
                
                # Add pathway classification
                self.flux_data['Pathway'] = self.flux_data['Reaction_ID'].apply(self._classify_pathway)
                
                return True
            else:
                print(f"✗ FBA failed with status: {self.solution.status}")
                return False
                
        except Exception as e:
            print(f"✗ Error in FBA: {e}")
            return False
    
    def _classify_pathway(self, reaction_id):
        """Classify reaction into metabolic pathway"""
        rxn_id_lower = reaction_id.lower()
        
        pathway_keywords = {
            'Glycolysis': ['pgi', 'pfk', 'fba', 'tpi', 'gapdh', 'pgk', 'pgm', 'eno', 'pyk', 'glc', 'g6p', 'f6p'],
            'TCA Cycle': ['cs', 'idh', 'akgdh', 'sucoas', 'sdh', 'fum', 'mdh', 'cit', 'succ', 'mal', 'oaa'],
            'Pentose Phosphate': ['6pgc', 'ru5p', 'x5p', 'r5p', 'g6pd', 'pentose', 'ribose'],
            'Amino Acid Metabolism': ['ala', 'gly', 'ser', 'thr', 'val', 'leu', 'ile', 'met', 'phe', 'tyr', 'trp'],
            'Nucleotide Metabolism': ['amp', 'gmp', 'cmp', 'ump', 'atp', 'gtp', 'ctp', 'utp', 'purine', 'pyrimidine'],
            'Transport': ['transport', 'abc', 'pts', 'permease', 't2pp', 't3pp'],
            'Exchange': ['ex_'],
            'Biomass': ['biomass'],
            'Other': []
        }
        
        for pathway, keywords in pathway_keywords.items():
            if any(keyword in rxn_id_lower for keyword in keywords):
                return pathway
        
        return 'Other'
    
    def create_network_fluxmap(self, top_n=50):
        """
        Create network graph with flux-weighted edges
        
        Args:
            top_n: Number of top reactions to include in the network
        """
        print("Creating network fluxmap...")
        
        # Get top reactions by absolute flux
        top_reactions = self.flux_data.nlargest(top_n, 'Abs_Flux')
        
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
            rxn = self.model.reactions.get_by_id(row['Reaction_ID'])
            
            # Find connected reactions through shared metabolites
            for met in rxn.metabolites:
                for connected_rxn in met.reactions:
                    if connected_rxn.id in top_reactions['Reaction_ID'].values:
                        if row['Reaction_ID'] != connected_rxn.id:
                            G.add_edge(row['Reaction_ID'], connected_rxn.id)
        
        # Create visualization
        plt.figure(figsize=(16, 12))
        
        # Position nodes using spring layout
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Define colors for different pathways
        pathway_colors = {
            'Glycolysis': '#FF6B6B',
            'TCA Cycle': '#4ECDC4',
            'Pentose Phosphate': '#45B7D1',
            'Amino Acid Metabolism': '#96CEB4',
            'Nucleotide Metabolism': '#FFEAA7',
            'Transport': '#DDA0DD',
            'Exchange': '#98D8C8',
            'Biomass': '#F7DC6F',
            'Other': '#BDC3C7'
        }
        
        # Draw nodes
        node_colors = [pathway_colors.get(G.nodes[node]['pathway'], '#BDC3C7') 
                      for node in G.nodes()]
        node_sizes = [abs(G.nodes[node]['flux']) * 1000 for node in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos, 
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, 
                              edge_color='gray',
                              alpha=0.3,
                              arrows=True,
                              arrowsize=10)
        
        # Add labels for important nodes
        important_nodes = [node for node in G.nodes() 
                          if abs(G.nodes[node]['flux']) > np.percentile([abs(G.nodes[n]['flux']) for n in G.nodes()], 75)]
        
        labels = {node: node for node in important_nodes}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
        
        # Create legend
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                     markerfacecolor=color, markersize=10, label=pathway)
                          for pathway, color in pathway_colors.items()]
        
        plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        plt.title(f'Metabolic Network Fluxmap\n(Top {top_n} Reactions by Flux)', 
                 fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # Save plot
        output_file = os.path.join(self.output_dir, 'network_fluxmap.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Network fluxmap saved to: {output_file}")
        plt.close()
    
    def create_pathway_heatmap(self):
        """Create heatmap of pathway fluxes"""
        print("Creating pathway flux heatmap...")
        
        # Group by pathway and calculate statistics
        pathway_stats = self.flux_data.groupby('Pathway').agg({
            'Flux_Value': ['mean', 'sum', 'std'],
            'Abs_Flux': ['mean', 'sum'],
            'Reaction_ID': 'count'
        }).round(4)
        
        pathway_stats.columns = ['Mean_Flux', 'Total_Flux', 'Std_Flux', 'Mean_Abs_Flux', 'Total_Abs_Flux', 'Reaction_Count']
        pathway_stats = pathway_stats.sort_values('Total_Abs_Flux', ascending=False)
        
        # Create heatmap
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Heatmap 1: Mean flux by pathway
        heatmap_data1 = pathway_stats[['Mean_Flux', 'Mean_Abs_Flux']].T
        sns.heatmap(heatmap_data1, annot=True, cmap='RdBu_r', center=0, 
                   fmt='.3f', ax=ax1, cbar_kws={'label': 'Flux Value'})
        ax1.set_title('Mean Flux by Pathway', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Metabolic Pathways')
        
        # Heatmap 2: Reaction count and total flux
        heatmap_data2 = pathway_stats[['Reaction_Count', 'Total_Abs_Flux']].T
        sns.heatmap(heatmap_data2, annot=True, cmap='YlOrRd', 
                   fmt='.1f', ax=ax2, cbar_kws={'label': 'Count/Flux'})
        ax2.set_title('Reaction Count and Total Flux by Pathway', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Metabolic Pathways')
        
        plt.tight_layout()
        output_file = os.path.join(self.output_dir, 'pathway_flux_heatmap.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Pathway heatmap saved to: {output_file}")
        plt.close()
        
        return pathway_stats
    
    def create_flux_distribution_plots(self):
        """Create various flux distribution plots"""
        print("Creating flux distribution plots...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Flux distribution histogram
        ax1.hist(self.flux_data['Flux_Value'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_xlabel('Flux Value')
        ax1.set_ylabel('Frequency')
        ax1.set_title('Flux Distribution')
        ax1.grid(True, alpha=0.3)
        
        # 2. Top reactions by flux
        top_reactions = self.flux_data.nlargest(15, 'Abs_Flux')
        y_pos = range(len(top_reactions))
        colors = ['red' if x < 0 else 'blue' for x in top_reactions['Flux_Value']]
        ax2.barh(y_pos, top_reactions['Flux_Value'], color=colors, alpha=0.7)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(top_reactions['Reaction_ID'], fontsize=8)
        ax2.set_xlabel('Flux Value')
        ax2.set_title('Top 15 Reactions by Flux')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # 3. Flux by pathway
        pathway_flux = self.flux_data.groupby('Pathway')['Abs_Flux'].sum().sort_values(ascending=False)
        ax3.bar(range(len(pathway_flux)), pathway_flux.values, color='lightgreen', alpha=0.7)
        ax3.set_xlabel('Metabolic Pathways')
        ax3.set_ylabel('Total Absolute Flux')
        ax3.set_title('Total Flux by Pathway')
        ax3.set_xticks(range(len(pathway_flux)))
        ax3.set_xticklabels(pathway_flux.index, rotation=45, ha='right')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. Exchange reactions
        exchange_rxns = self.flux_data[self.flux_data['Pathway'] == 'Exchange']
        if len(exchange_rxns) > 0:
            top_exchanges = exchange_rxns.nlargest(10, 'Abs_Flux')
            y_pos = range(len(top_exchanges))
            colors = ['red' if x < 0 else 'blue' for x in top_exchanges['Flux_Value']]
            ax4.barh(y_pos, top_exchanges['Flux_Value'], color=colors, alpha=0.7)
            ax4.set_yticks(y_pos)
            ax4.set_yticklabels(top_exchanges['Reaction_ID'], fontsize=8)
            ax4.set_xlabel('Flux Value')
            ax4.set_title('Top Exchange Reactions')
            ax4.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        output_file = os.path.join(self.output_dir, 'flux_distribution_plots.png')
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Flux distribution plots saved to: {output_file}")
        plt.close()
    
    def create_sankey_diagram(self):
        """Create Sankey diagram of major metabolic pathways"""
        print("Creating Sankey diagram...")
        
        try:
            import plotly.graph_objects as go
            
            # Get major pathways
            pathway_flux = self.flux_data.groupby('Pathway')['Abs_Flux'].sum().sort_values(ascending=False)
            major_pathways = pathway_flux.head(8).index.tolist()
            
            # Create source-target pairs
            sources = []
            targets = []
            values = []
            
            # Add connections from input to pathways
            for pathway in major_pathways:
                pathway_flux_sum = pathway_flux[pathway]
                sources.append("Input")
                targets.append(pathway)
                values.append(pathway_flux_sum)
            
            # Add connections from pathways to output
            for pathway in major_pathways:
                pathway_flux_sum = pathway_flux[pathway]
                sources.append(pathway)
                targets.append("Output")
                values.append(pathway_flux_sum)
            
            # Create Sankey diagram
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=["Input"] + major_pathways + ["Output"],
                    color="blue"
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values
                )
            )])
            
            fig.update_layout(
                title_text="Metabolic Pathway Flux Distribution (Sankey Diagram)",
                font_size=10,
                height=600
            )
            
            # Save as HTML for interactive viewing
            output_file = os.path.join(self.output_dir, 'sankey_diagram.html')
            fig.write_html(output_file)
            print(f"✓ Sankey diagram saved to: {output_file}")
            
        except ImportError:
            print("⚠️ Plotly not available. Skipping Sankey diagram.")
    
    def save_flux_data(self):
        """Save flux data to CSV files"""
        print("Saving flux data...")
        
        # Save complete flux data
        flux_file = os.path.join(self.output_dir, 'complete_flux_data.csv')
        self.flux_data.to_csv(flux_file, index=False)
        print(f"✓ Complete flux data saved to: {flux_file}")
        
        # Save pathway summary
        pathway_summary = self.flux_data.groupby('Pathway').agg({
            'Flux_Value': ['count', 'mean', 'sum', 'std'],
            'Abs_Flux': ['mean', 'sum']
        }).round(4)
        
        pathway_summary.columns = ['Reaction_Count', 'Mean_Flux', 'Total_Flux', 'Std_Flux', 'Mean_Abs_Flux', 'Total_Abs_Flux']
        pathway_summary = pathway_summary.sort_values('Total_Abs_Flux', ascending=False)
        
        summary_file = os.path.join(self.output_dir, 'pathway_summary.csv')
        pathway_summary.to_csv(summary_file)
        print(f"✓ Pathway summary saved to: {summary_file}")
    
    def generate_comprehensive_fluxmap(self):
        """Generate all fluxmap visualizations"""
        print("="*60)
        print("Generating Comprehensive Metabolic Fluxmap")
        print("="*60)
        
        # Load model
        if not self.load_model():
            return False
        
        # Perform FBA
        if not self.perform_fba():
            return False
        
        # Create visualizations
        self.create_network_fluxmap()
        pathway_stats = self.create_pathway_heatmap()
        self.create_flux_distribution_plots()
        self.create_sankey_diagram()
        
        # Save data
        self.save_flux_data()
        
        print("\n" + "="*60)
        print("✓ Fluxmap generation completed!")
        print(f"Results saved in: {self.output_dir}")
        print("="*60)
        
        return True

def main():
    """Main function to demonstrate fluxmap visualization"""
    
    # Example usage with E. coli core model
    model_path = "downloads/e_coli_core.mat"  # Update this path to your model file
    
    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        print("Please update the model_path variable to point to your .mat file")
        return
    
    # Create visualizer
    visualizer = MetabolicFluxmapVisualizer(model_path)
    
    # Generate comprehensive fluxmap
    success = visualizer.generate_comprehensive_fluxmap()
    
    if success:
        print("\nGenerated files:")
        for file in os.listdir(visualizer.output_dir):
            print(f"  - {file}")
    else:
        print("Fluxmap generation failed!")

if __name__ == "__main__":
    main()
