#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COBRA Visual Agent

This agent specializes in creating metabolic network visualizations and fluxmaps
from COBRA model files (.mat format). It provides comprehensive visualization
capabilities including network graphs, fluxmaps, and pathway analysis.

Features:
1. Load metabolic models from .mat files
2. Generate metabolic network graphs
3. Create fluxmap visualizations with flux data
4. Perform pathway analysis and classification
5. Generate comprehensive visualization reports

Author: BioLLM Team
Date: 2024
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import cobra
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.base import BaseAgent

class CobraVisualAgent(BaseAgent):
    """
    COBRA Visual Agent for metabolic network and fluxmap visualization
    """
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.solution = None
        self.flux_data = None
        self.output_dir = None
        
        # Set plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Pathway classification keywords
        self.pathway_keywords = {
            'Glycolysis': ['pgi', 'pfk', 'fba', 'tpi', 'gapdh', 'pgk', 'pgm', 'eno', 'pyk', 'glc', 'g6p', 'f6p'],
            'TCA Cycle': ['cs', 'idh', 'akgdh', 'sucoas', 'sdh', 'fum', 'mdh', 'cit', 'succ', 'mal', 'oaa'],
            'Pentose Phosphate': ['6pgc', 'ru5p', 'x5p', 'r5p', 'g6pd', 'pentose', 'ribose'],
            'Amino Acid Metabolism': ['ala', 'gly', 'ser', 'thr', 'val', 'leu', 'ile', 'met', 'phe', 'tyr', 'trp', 'his', 'arg', 'lys', 'asp', 'glu', 'cys', 'asn', 'gln', 'pro'],
            'Nucleotide Metabolism': ['amp', 'gmp', 'cmp', 'ump', 'atp', 'gtp', 'ctp', 'utp', 'adp', 'gdp', 'cdp', 'udp', 'purine', 'pyrimidine'],
            'Lipid Metabolism': ['fatty', 'acyl', 'coa', 'lipid', 'phospholipid'],
            'Transport': ['transport', 'abc', 'pts', 'permease', 't2pp', 't3pp'],
            'Exchange': ['ex_'],
            'Biomass': ['biomass'],
            'Other': []
        }
        
        # Pathway colors
        self.pathway_colors = {
            'Glycolysis': '#FF6B6B',
            'TCA Cycle': '#4ECDC4',
            'Pentose Phosphate': '#45B7D1',
            'Amino Acid Metabolism': '#96CEB4',
            'Nucleotide Metabolism': '#FFEAA7',
            'Lipid Metabolism': '#DDA0DD',
            'Transport': '#98D8C8',
            'Exchange': '#F7DC6F',
            'Biomass': '#E74C3C',
            'Other': '#BDC3C7'
        }
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process visualization request
        
        Args:
            request: Dictionary containing request parameters
                - model_path: Path to the .mat file
                - output_dir: Output directory for results
                - visualization_types: List of visualization types to generate
                - analysis_level: Level of analysis (basic, intermediate, comprehensive)
        
        Returns:
            Dictionary containing results and file paths
        """
        try:
            # Extract parameters
            model_path = request.get('model_path')
            output_dir = request.get('output_dir', 'cobra_visual_results')
            visualization_types = request.get('visualization_types', ['network', 'fluxmap', 'analysis'])
            analysis_level = request.get('analysis_level', 'comprehensive')
            
            # Validate input
            if not model_path or not os.path.exists(model_path):
                return {
                    'success': False,
                    'error': f'Model file not found: {model_path}',
                    'results': {}
                }
            
            # Create output directory
            self.output_dir = output_dir
            os.makedirs(output_dir, exist_ok=True)
            
            # Load model
            if not self._load_model(model_path):
                return {
                    'success': False,
                    'error': 'Failed to load metabolic model',
                    'results': {}
                }
            
            # Perform FBA
            if not self._perform_fba():
                return {
                    'success': False,
                    'error': 'Failed to perform FBA analysis',
                    'results': {}
                }
            
            # Generate visualizations
            results = {}
            
            if 'network' in visualization_types:
                results['network_graph'] = self._create_network_graph()
            
            if 'fluxmap' in visualization_types:
                results['fluxmap'] = self._create_fluxmap_visualization()
            
            if 'analysis' in visualization_types:
                results['analysis'] = self._create_comprehensive_analysis()
            
            # Generate summary report
            results['summary_report'] = self._generate_summary_report()
            
            return {
                'success': True,
                'model_info': self._get_model_info(),
                'results': results,
                'output_directory': output_dir
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error in COBRA visual agent: {str(e)}',
                'results': {}
            }
    
    def _load_model(self, model_path: str) -> bool:
        """Load metabolic model from .mat file"""
        try:
            print(f"Loading metabolic model from: {model_path}")
            self.model = cobra.io.load_matlab_model(model_path)
            
            print(f"✓ Model loaded successfully!")
            print(f"  - Model ID: {self.model.id}")
            print(f"  - Reactions: {len(self.model.reactions)}")
            print(f"  - Metabolites: {len(self.model.metabolites)}")
            print(f"  - Genes: {len(self.model.genes)}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error loading model: {e}")
            return False
    
    def _perform_fba(self) -> bool:
        """Perform Flux Balance Analysis"""
        try:
            print("Performing FBA analysis...")
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
    
    def _classify_pathway(self, reaction_id: str) -> str:
        """Classify reaction into metabolic pathway"""
        rxn_id_lower = reaction_id.lower()
        
        for pathway, keywords in self.pathway_keywords.items():
            if any(keyword in rxn_id_lower for keyword in keywords):
                return pathway
        
        return 'Other'
    
    def _create_network_graph(self) -> Dict[str, str]:
        """Create basic metabolic network graph"""
        print("Creating metabolic network graph...")
        
        try:
            # Create network graph
            G = nx.DiGraph()
            
            # Add nodes (reactions)
            for rxn in self.model.reactions:
                G.add_node(rxn.id, 
                          name=rxn.name,
                          pathway=self._classify_pathway(rxn.id))
            
            # Add edges based on metabolite connections
            for rxn in self.model.reactions:
                for met in rxn.metabolites:
                    for connected_rxn in met.reactions:
                        if rxn.id != connected_rxn.id:
                            G.add_edge(rxn.id, connected_rxn.id)
            
            # Create visualization with optimized size for Streamlit
            plt.figure(figsize=(12, 8))
            
            # Position nodes using spring layout
            pos = nx.spring_layout(G, k=1, iterations=30)
            
            # Draw nodes
            node_colors = [self.pathway_colors.get(G.nodes[node]['pathway'], '#BDC3C7') 
                          for node in G.nodes()]
            
            nx.draw_networkx_nodes(G, pos, 
                                  node_color=node_colors,
                                  node_size=50,
                                  alpha=0.7)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, 
                                  edge_color='gray',
                                  alpha=0.2,
                                  arrows=True,
                                  arrowsize=5)
            
            # Create legend
            legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                         markerfacecolor=color, markersize=8, label=pathway)
                              for pathway, color in self.pathway_colors.items()]
            
            plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
            plt.title(f'Metabolic Network Graph - {self.model.id}', 
                     fontsize=16, fontweight='bold')
            plt.axis('off')
            
            # Save plot with optimized settings for Streamlit
            output_file = os.path.join(self.output_dir, 'metabolic_network_graph.png')
            plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
            plt.close()
            
            # Convert to RGB for better Streamlit compatibility
            try:
                from PIL import Image
                with Image.open(output_file) as img:
                    if img.mode == 'RGBA':
                        # Create white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        background.save(output_file, 'PNG', optimize=True)
            except Exception as e:
                print(f"Warning: Could not convert image to RGB: {e}")
            
            print(f"✓ Network graph saved to: {output_file}")
            
            return {
                'network_graph': output_file,
                'node_count': len(G.nodes()),
                'edge_count': len(G.edges())
            }
            
        except Exception as e:
            print(f"✗ Error creating network graph: {e}")
            return {'error': str(e)}
    
    def _create_fluxmap_visualization(self) -> Dict[str, str]:
        """Create fluxmap visualization with flux data"""
        print("Creating fluxmap visualization...")
        
        try:
            # Get top reactions by flux
            top_reactions = self.flux_data.nlargest(50, 'Abs_Flux')
            
            # Create network graph for fluxmap
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
            
            # Create visualization with optimized size for Streamlit
            plt.figure(figsize=(12, 8))
            
            # Position nodes using spring layout
            pos = nx.spring_layout(G, k=3, iterations=50)
            
            # Draw nodes with flux-weighted sizes
            node_colors = [self.pathway_colors.get(G.nodes[node]['pathway'], '#BDC3C7') 
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
                              for pathway, color in self.pathway_colors.items()]
            
            plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
            plt.title(f'Metabolic Network Fluxmap - {self.model.id}\n(Node size = Flux magnitude)', 
                     fontsize=16, fontweight='bold')
            plt.axis('off')
            
            # Save plot with optimized settings for Streamlit
            output_file = os.path.join(self.output_dir, 'metabolic_fluxmap.png')
            plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
            plt.close()
            
            # Convert to RGB for better Streamlit compatibility
            try:
                from PIL import Image
                with Image.open(output_file) as img:
                    if img.mode == 'RGBA':
                        # Create white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        background.save(output_file, 'PNG', optimize=True)
            except Exception as e:
                print(f"Warning: Could not convert image to RGB: {e}")
            
            print(f"✓ Fluxmap saved to: {output_file}")
            
            return {
                'fluxmap': output_file,
                'top_reactions_count': len(top_reactions),
                'max_flux': top_reactions['Abs_Flux'].max()
            }
            
        except Exception as e:
            print(f"✗ Error creating fluxmap: {e}")
            return {'error': str(e)}
    
    def _create_comprehensive_analysis(self) -> Dict[str, str]:
        """Create comprehensive analysis visualizations"""
        print("Creating comprehensive analysis...")
        
        try:
            results = {}
            
            # 1. Pathway flux heatmap
            pathway_stats = self.flux_data.groupby('Pathway').agg({
                'Flux_Value': ['mean', 'sum', 'std'],
                'Abs_Flux': ['mean', 'sum'],
                'Reaction_ID': 'count'
            }).round(4)
            
            pathway_stats.columns = ['Mean_Flux', 'Total_Flux', 'Std_Flux', 'Mean_Abs_Flux', 'Total_Abs_Flux', 'Reaction_Count']
            pathway_stats = pathway_stats.sort_values('Total_Abs_Flux', ascending=False)
            
            # Create heatmap with optimized size for Streamlit
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            
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
            heatmap_file = os.path.join(self.output_dir, 'pathway_flux_heatmap.png')
            plt.savefig(heatmap_file, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
            plt.close()
            
            # Convert to RGB for better Streamlit compatibility
            try:
                from PIL import Image
                with Image.open(heatmap_file) as img:
                    if img.mode == 'RGBA':
                        # Create white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        background.save(heatmap_file, 'PNG', optimize=True)
            except Exception as e:
                print(f"Warning: Could not convert image to RGB: {e}")
            
            results['pathway_heatmap'] = heatmap_file
            
            # 2. Flux distribution plots with optimized size for Streamlit
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 9))
            
            # Flux distribution histogram
            ax1.hist(self.flux_data['Flux_Value'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
            ax1.set_xlabel('Flux Value')
            ax1.set_ylabel('Frequency')
            ax1.set_title('Flux Distribution')
            ax1.grid(True, alpha=0.3)
            
            # Top reactions by flux
            top_reactions = self.flux_data.nlargest(15, 'Abs_Flux')
            y_pos = range(len(top_reactions))
            colors = ['red' if x < 0 else 'blue' for x in top_reactions['Flux_Value']]
            ax2.barh(y_pos, top_reactions['Flux_Value'], color=colors, alpha=0.7)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(top_reactions['Reaction_ID'], fontsize=8)
            ax2.set_xlabel('Flux Value')
            ax2.set_title('Top 15 Reactions by Flux')
            ax2.grid(True, alpha=0.3, axis='x')
            
            # Flux by pathway
            pathway_flux = self.flux_data.groupby('Pathway')['Abs_Flux'].sum().sort_values(ascending=False)
            ax3.bar(range(len(pathway_flux)), pathway_flux.values, color='lightgreen', alpha=0.7)
            ax3.set_xlabel('Metabolic Pathways')
            ax3.set_ylabel('Total Absolute Flux')
            ax3.set_title('Total Flux by Pathway')
            ax3.set_xticks(range(len(pathway_flux)))
            ax3.set_xticklabels(pathway_flux.index, rotation=45, ha='right')
            ax3.grid(True, alpha=0.3, axis='y')
            
            # Exchange reactions
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
            distribution_file = os.path.join(self.output_dir, 'flux_distribution_plots.png')
            plt.savefig(distribution_file, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
            plt.close()
            
            # Convert to RGB for better Streamlit compatibility
            try:
                from PIL import Image
                with Image.open(distribution_file) as img:
                    if img.mode == 'RGBA':
                        # Create white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        background.save(distribution_file, 'PNG', optimize=True)
            except Exception as e:
                print(f"Warning: Could not convert image to RGB: {e}")
            
            results['flux_distribution'] = distribution_file
            
            # 3. Save data files
            flux_file = os.path.join(self.output_dir, 'complete_flux_data.csv')
            self.flux_data.to_csv(flux_file, index=False)
            results['flux_data'] = flux_file
            
            summary_file = os.path.join(self.output_dir, 'pathway_summary.csv')
            pathway_stats.to_csv(summary_file)
            results['pathway_summary'] = summary_file
            
            print(f"✓ Comprehensive analysis completed")
            
            return results
            
        except Exception as e:
            print(f"✗ Error in comprehensive analysis: {e}")
            return {'error': str(e)}
    
    def _get_model_info(self) -> Dict[str, Any]:
        """Get basic model information"""
        return {
            'model_id': self.model.id,
            'model_name': getattr(self.model, 'name', 'Unknown'),
            'reactions_count': len(self.model.reactions),
            'metabolites_count': len(self.model.metabolites),
            'genes_count': len(self.model.genes),
            'compartments': list(self.model.compartments.keys()),
            'objective_function': str(self.model.objective),
            'fba_status': self.solution.status if self.solution else 'Not performed',
            'growth_rate': self.solution.objective_value if self.solution else None
        }
    
    def _generate_summary_report(self) -> str:
        """Generate summary report"""
        print("Generating summary report...")
        
        try:
            report_file = os.path.join(self.output_dir, 'visualization_report.html')
            
            # Get model info
            model_info = self._get_model_info()
            
            # Get pathway statistics
            pathway_stats = self.flux_data.groupby('Pathway').agg({
                'Reaction_ID': 'count',
                'Abs_Flux': 'sum'
            }).round(4)
            pathway_stats.columns = ['Reaction_Count', 'Total_Abs_Flux']
            pathway_stats = pathway_stats.sort_values('Total_Abs_Flux', ascending=False)
            
            # Create HTML report
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>COBRA Visual Analysis Report - {model_info['model_id']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 10px; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .visualization {{ margin: 20px 0; text-align: center; }}
                    .visualization img {{ max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4f8; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🧬 COBRA Visual Analysis Report</h1>
                    <h2>Model: {model_info['model_id']}</h2>
                    <p>Generated by COBRA Visual Agent</p>
                </div>
                
                <div class="section">
                    <h2>📊 Model Information</h2>
                    <div class="metric"><strong>Reactions:</strong> {model_info['reactions_count']}</div>
                    <div class="metric"><strong>Metabolites:</strong> {model_info['metabolites_count']}</div>
                    <div class="metric"><strong>Genes:</strong> {model_info['genes_count']}</div>
                    <div class="metric"><strong>Growth Rate:</strong> {model_info['growth_rate']:.6f} h⁻¹</div>
                </div>
                

                
                <div class="section">
                    <h2>📈 Metabolic Fluxmap</h2>
                    <div class="visualization">
                        <img src="metabolic_fluxmap.png" alt="Metabolic Fluxmap">
                        <p><em>Fluxmap showing flux distribution with node size proportional to flux magnitude</em></p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🔥 Pathway Flux Analysis</h2>
                    <div class="visualization">
                        <img src="pathway_flux_heatmap.png" alt="Pathway Flux Heatmap">
                        <p><em>Heatmap showing flux statistics by metabolic pathway</em></p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📊 Flux Distribution Analysis</h2>
                    <div class="visualization">
                        <img src="flux_distribution_plots.png" alt="Flux Distribution Plots">
                        <p><em>Comprehensive flux distribution analysis including histograms and pathway comparisons</em></p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📋 Pathway Summary</h2>
                    <table>
                        <tr>
                            <th>Pathway</th>
                            <th>Reaction Count</th>
                            <th>Total Absolute Flux</th>
                        </tr>
                        {''.join([f'<tr><td>{pathway}</td><td>{stats["Reaction_Count"]}</td><td>{stats["Total_Abs_Flux"]:.4f}</td></tr>' for pathway, stats in pathway_stats.iterrows()])}
                    </table>
                </div>
                
                <div class="section">
                    <h2>📁 Generated Files</h2>
                    <ul>
                        <li><strong>metabolic_network_graph.png</strong> - Complete metabolic network visualization</li>
                        <li><strong>metabolic_fluxmap.png</strong> - Fluxmap with flux-weighted nodes</li>
                        <li><strong>pathway_flux_heatmap.png</strong> - Pathway flux analysis heatmap</li>
                        <li><strong>flux_distribution_plots.png</strong> - Comprehensive flux distribution analysis</li>
                        <li><strong>complete_flux_data.csv</strong> - Complete flux data for all reactions</li>
                        <li><strong>pathway_summary.csv</strong> - Pathway-level statistics</li>
                    </ul>
                </div>
            </body>
            </html>
            """
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✓ Summary report saved to: {report_file}")
            
            return report_file
            
        except Exception as e:
            print(f"✗ Error generating summary report: {e}")
            return ""

# Example usage function
def create_cobra_visualization(model_path: str, output_dir: str = "cobra_visual_results") -> Dict[str, Any]:
    """
    Convenience function to create COBRA visualizations
    
    Args:
        model_path: Path to the .mat file
        output_dir: Output directory for results
        
    Returns:
        Dictionary containing results and file paths
    """
    agent = CobraVisualAgent()
    
    request = {
        'model_path': model_path,
        'output_dir': output_dir,
        'visualization_types': ['network', 'fluxmap', 'analysis'],
        'analysis_level': 'comprehensive'
    }
    
    return agent.process_request(request)

if __name__ == "__main__":
    # Example usage
    model_path = "downloads/e_coli_core.mat"  # Update this path
    
    if os.path.exists(model_path):
        result = create_cobra_visualization(model_path)
        if result['success']:
            print("✓ COBRA visualization completed successfully!")
            print(f"Results saved in: {result['output_directory']}")
        else:
            print(f"✗ Error: {result['error']}")
    else:
        print(f"Model file not found: {model_path}")
        print("Please update the model_path variable to point to your .mat file")
