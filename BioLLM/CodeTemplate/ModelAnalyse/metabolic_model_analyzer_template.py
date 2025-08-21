#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metabolic Network Model Analysis Template

This template integrates complete metabolic model analysis functionality, including:
1. Model basic information retrieval
2. Reaction count statistics
3. Reaction classification analysis
4. Metabolic pathway distribution analysis
5. Core pathway detailed analysis
6. Visualization chart generation

Usage:
1. Configure SLOT_MODEL_PATH to your model file path
2. Configure SLOT_OUTPUT_DIR to your desired output directory
3. Run the script to get complete analysis results

Author: BioLLM Team
Date: 2024
"""

# =============================================================================
# CONFIGURATION SECTION
# =============================================================================

# SLOT: Model file path - Please modify to your model file path
SLOT_MODEL_PATH = "downloads/your_model_file.xml"  # Supports .xml, .json, .mat formats

# SLOT: Output directory - Please modify to your desired output directory
SLOT_OUTPUT_DIR = "analysis_results"

# SLOT: Model name - Used for report and chart titles
SLOT_MODEL_NAME = "Your Model Name"

# SLOT: Whether to generate visualization charts (True/False)
SLOT_GENERATE_VISUALIZATIONS = True

# SLOT: Whether to save detailed report (True/False)
SLOT_SAVE_REPORT = True

# SLOT: Custom metabolic pathway keywords (optional)
SLOT_CUSTOM_PATHWAYS = {
    # You can add custom metabolic pathway keywords here
    # 'Custom Pathway': ['keyword1', 'keyword2', 'keyword3']
}

# =============================================================================
# IMPORT NECESSARY LIBRARIES
# =============================================================================

import cobra
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from pathlib import Path

# Set font support
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# =============================================================================
# MODEL LOADING FUNCTION
# =============================================================================

def load_metabolic_model(model_path):
    """
    Load metabolic model, supports multiple formats and loading methods
    
    Args:
        model_path (str): Model file path
        
    Returns:
        cobra.Model: Loaded metabolic model
    """
    print(f"Loading model: {model_path}")
    
    # Check if file exists
    if not os.path.exists(model_path):
        print(f"Error: Model file does not exist - {model_path}")
        return None
    
    # Choose loading method based on file extension
    file_ext = Path(model_path).suffix.lower()
    
    try:
        if file_ext == '.xml':
            model = cobra.io.read_sbml_model(model_path)
        elif file_ext == '.json':
            model = cobra.io.load_json_model(model_path)
        elif file_ext == '.mat':
            model = cobra.io.load_matlab_model(model_path)
        else:
            # Try universal loading method
            model = cobra.io.load_model(model_path)
        
        print(f"✓ Successfully loaded model: {model.id}")
        print(f"  Model name: {model.name}")
        print(f"  Reaction count: {len(model.reactions)}")
        print(f"  Metabolite count: {len(model.metabolites)}")
        print(f"  Gene count: {len(model.genes)}")
        
        return model
        
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Trying alternative loading method...")
        
        try:
            # Try loading from BiGG Models
            model_name = Path(model_path).stem
            model = cobra.io.load_model(model_name)
            print(f"✓ Successfully loaded model from BiGG Models: {model_name}")
            return model
        except Exception as e2:
            print(f"Alternative loading method also failed: {e2}")
            print("Using E. coli core model as example...")
            
            try:
                model = cobra.test.create_test_model("ecoli")
                print(f"Using E. coli core model as example")
                return model
            except:
                print("Unable to load any model")
                return None

# =============================================================================
# BASIC INFORMATION ANALYSIS FUNCTION
# =============================================================================

def analyze_basic_info(model):
    """
    Analyze basic information of the model
    
    Args:
        model: cobra.Model object
        
    Returns:
        dict: Dictionary containing basic information
    """
    print("\n=== Model Basic Information Analysis ===")
    
    basic_info = {
        'model_id': model.id,
        'model_name': model.name,
        'reactions_count': len(model.reactions),
        'metabolites_count': len(model.metabolites),
        'genes_count': len(model.genes),
        'compartments': list(model.compartments.keys())
    }
    
    print(f"Model ID: {basic_info['model_id']}")
    print(f"Model name: {basic_info['model_name']}")
    print(f"Reaction count: {basic_info['reactions_count']}")
    print(f"Metabolite count: {basic_info['metabolites_count']}")
    print(f"Gene count: {basic_info['genes_count']}")
    print(f"Compartments: {', '.join(basic_info['compartments'])}")
    
    return basic_info

# =============================================================================
# REACTION CLASSIFICATION ANALYSIS FUNCTION
# =============================================================================

def analyze_reaction_classification(model):
    """
    Perform reaction classification analysis
    
    Args:
        model: cobra.Model object
        
    Returns:
        dict: Dictionary containing reaction classification statistics
    """
    print("\n=== Reaction Classification Analysis ===")
    
    # Initialize counters
    reaction_prefixes = defaultdict(int)
    exchange_reactions = 0
    transport_reactions = 0
    biomass_reactions = 0
    maintenance_reactions = 0
    
    # Analyze each reaction
    for rxn in model.reactions:
        rxn_id = rxn.id.lower()
        
        # Classify reactions
        if rxn_id.startswith('ex_'):
            exchange_reactions += 1
        elif 'biomass' in rxn_id:
            biomass_reactions += 1
        elif 'atpm' in rxn_id or 'maintenance' in rxn_id:
            maintenance_reactions += 1
        elif any(word in rxn_id for word in ['transport', 'abc', 'pts']):
            transport_reactions += 1
        
        # Count prefixes
        if '_' in rxn_id:
            prefix = rxn_id.split('_')[0]
            reaction_prefixes[prefix] += 1
    
    # Calculate internal reaction count
    internal_reactions = len(model.reactions) - exchange_reactions - transport_reactions - biomass_reactions - maintenance_reactions
    
    classification_stats = {
        'exchange_reactions': exchange_reactions,
        'transport_reactions': transport_reactions,
        'biomass_reactions': biomass_reactions,
        'maintenance_reactions': maintenance_reactions,
        'internal_reactions': internal_reactions,
        'reaction_prefixes': dict(reaction_prefixes)
    }
    
    print(f"Exchange reactions (EX_): {exchange_reactions}")
    print(f"Transport reactions: {transport_reactions}")
    print(f"Biomass reactions: {biomass_reactions}")
    print(f"Maintenance reactions: {maintenance_reactions}")
    print(f"Internal reactions: {internal_reactions}")
    
    print(f"\nTop reaction prefixes (top 15):")
    sorted_prefixes = sorted(reaction_prefixes.items(), key=lambda x: x[1], reverse=True)
    for prefix, count in sorted_prefixes[:15]:
        print(f"  {prefix}: {count}")
    
    return classification_stats

# =============================================================================
# METABOLIC PATHWAY DISTRIBUTION ANALYSIS FUNCTION
# =============================================================================

def analyze_pathway_distribution(model, custom_pathways=None):
    """
    Analyze metabolic pathway distribution
    
    Args:
        model: cobra.Model object
        custom_pathways: Custom metabolic pathway keyword dictionary
        
    Returns:
        dict: Dictionary containing pathway distribution statistics
    """
    print("\n=== Metabolic Pathway Distribution Analysis ===")
    
    # Define standard metabolic pathway keywords
    standard_pathways = {
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
    
    # Merge custom pathways
    if custom_pathways:
        standard_pathways.update(custom_pathways)
    
    # Count reactions for each pathway
    pathway_counts = defaultdict(int)
    
    for rxn in model.reactions:
        rxn_name_lower = rxn.name.lower()
        rxn_id_lower = rxn.id.lower()
        
        # Get metabolites in reaction
        metabolites = [met.id.lower() for met in rxn.metabolites]
        all_text = rxn_name_lower + ' ' + rxn_id_lower + ' ' + ' '.join(metabolites)
        
        matched_pathways = []
        for pathway, keywords in standard_pathways.items():
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
        print(f"{pathway:<20} {count:4d} reactions ({percentage:5.1f}%)")
    
    return {
        'pathway_counts': dict(pathway_counts),
        'sorted_pathways': sorted_pathways,
        'total_reactions': total_reactions
    }

# =============================================================================
# CORE PATHWAY DETAILED ANALYSIS FUNCTION
# =============================================================================

def analyze_core_pathways(model):
    """
    Detailed analysis of core metabolic pathways
    
    Args:
        model: cobra.Model object
        
    Returns:
        dict: Dictionary containing core pathway analysis results
    """
    print("\n=== Core Metabolic Pathway Detailed Analysis ===")
    
    # Glycolysis pathway key reactions
    print("1. Glycolysis pathway key reactions:")
    print("-" * 40)
    glycolysis_reactions = []
    for rxn in model.reactions:
        if any(keyword in rxn.id.lower() or keyword in rxn.name.lower() 
               for keyword in ['pgi', 'pfk', 'fba', 'tpi', 'gapdh', 'pgk', 'pgm', 'eno', 'pyk']):
            glycolysis_reactions.append(rxn)
    
    for rxn in glycolysis_reactions[:10]:
        print(f"ID: {rxn.id:10} | {rxn.name}")
    
    # TCA cycle key reactions
    print(f"\n2. TCA cycle key reactions:")
    print("-" * 40)
    tca_reactions = []
    for rxn in model.reactions:
        if any(keyword in rxn.id.lower() or keyword in rxn.name.lower()
               for keyword in ['cs', 'idh', 'akgdh', 'sucoas', 'sdh', 'fum', 'mdh']):
            tca_reactions.append(rxn)
    
    for rxn in tca_reactions[:10]:
        print(f"ID: {rxn.id:10} | {rxn.name}")
    
    # Exchange reactions
    print(f"\n3. Important exchange reactions (nutrients and products):")
    print("-" * 40)
    exchange_rxns = [rxn for rxn in model.reactions if rxn.id.startswith('EX_')]
    important_exchanges = []
    for rxn in exchange_rxns:
        if any(nutrient in rxn.id.lower() for nutrient in ['glc', 'o2', 'pi', 'so4', 'nh4', 'co2', 'h2o']):
            important_exchanges.append(rxn)
    
    for rxn in important_exchanges[:15]:
        print(f"ID: {rxn.id:15} | {rxn.name}")
    
    return {
        'glycolysis_reactions': glycolysis_reactions,
        'tca_reactions': tca_reactions,
        'important_exchanges': important_exchanges
    }

# =============================================================================
# VISUALIZATION FUNCTION
# =============================================================================

def create_visualizations(model, basic_info, classification_stats, pathway_data, output_dir):
    """
    Create visualization charts
    
    Args:
        model: cobra.Model object
        basic_info: Basic information dictionary
        classification_stats: Reaction classification statistics dictionary
        pathway_data: Pathway distribution data dictionary
        output_dir: Output directory
    """
    print("\n=== Creating Metabolic Network Visualization ===")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Set chart style
    plt.style.use('default')
    
    # Create 2x2 subplot layout
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Metabolic pathway distribution pie chart
    pathway_names = [name for name, count in pathway_data['sorted_pathways'] if count > 50]
    pathway_values = [count for name, count in pathway_data['sorted_pathways'] if count > 50]
    other_count = sum([count for name, count in pathway_data['sorted_pathways'] if count <= 50])
    
    if other_count > 0:
        pathway_names.append('Other')
        pathway_values.append(other_count)
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(pathway_names)))
    ax1.pie(pathway_values, labels=pathway_names, autopct='%1.1f%%', colors=colors, startangle=90)
    ax1.set_title(f'{SLOT_MODEL_NAME} Metabolic Pathway Distribution', fontsize=14, fontweight='bold')
    
    # 2. Main pathway reaction count bar chart
    ax2.bar(range(len(pathway_names)), pathway_values, color=colors)
    ax2.set_xlabel('Metabolic Pathways')
    ax2.set_ylabel('Reaction Count')
    ax2.set_title('Main Metabolic Pathway Reaction Counts', fontsize=14, fontweight='bold')
    ax2.set_xticks(range(len(pathway_names)))
    ax2.set_xticklabels(pathway_names, rotation=45, ha='right')
    
    # 3. Basic statistics
    stats = {
        'Reactions': basic_info['reactions_count'],
        'Metabolites': basic_info['metabolites_count'], 
        'Genes': basic_info['genes_count'],
        'Exchange Reactions': classification_stats['exchange_reactions'],
        'Transport Reactions': classification_stats['transport_reactions']
    }
    
    ax3.bar(stats.keys(), stats.values(), color='skyblue')
    ax3.set_ylabel('Count')
    ax3.set_title(f'{SLOT_MODEL_NAME} Model Basic Statistics', fontsize=14, fontweight='bold')
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Reaction type distribution
    reaction_types = {
        'Exchange Reactions': classification_stats['exchange_reactions'],
        'Transport Reactions': classification_stats['transport_reactions'],
        'Biomass Reactions': classification_stats['biomass_reactions'],
        'Maintenance Reactions': classification_stats['maintenance_reactions'],
        'Internal Reactions': classification_stats['internal_reactions']
    }
    
    ax4.bar(reaction_types.keys(), reaction_types.values(), color='lightcoral')
    ax4.set_ylabel('Reaction Count')
    ax4.set_title('Reaction Type Distribution', fontsize=14, fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, f'{SLOT_MODEL_NAME}_metabolic_network_overview.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Metabolic network overview chart saved to: {output_file}")
    plt.close()

# =============================================================================
# REPORT GENERATION FUNCTION
# =============================================================================

def generate_report(model, basic_info, classification_stats, pathway_data, core_pathways, output_dir):
    """
    Generate detailed analysis report
    
    Args:
        model: cobra.Model object
        basic_info: Basic information dictionary
        classification_stats: Reaction classification statistics dictionary
        pathway_data: Pathway distribution data dictionary
        core_pathways: Core pathway analysis results dictionary
        output_dir: Output directory
    """
    print(f"\n=== Generating Detailed Analysis Report ===")
    
    report_file = os.path.join(output_dir, f'{SLOT_MODEL_NAME}_analysis_report.txt')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"{SLOT_MODEL_NAME} Metabolic Network Model Analysis Report\n")
        f.write("="*50 + "\n\n")
        
        f.write("Basic Information:\n")
        f.write(f"- Model ID: {basic_info['model_id']}\n")
        f.write(f"- Model name: {basic_info['model_name']}\n")
        f.write(f"- Reaction count: {basic_info['reactions_count']}\n")
        f.write(f"- Metabolite count: {basic_info['metabolites_count']}\n") 
        f.write(f"- Gene count: {basic_info['genes_count']}\n")
        f.write(f"- Compartments: {', '.join(basic_info['compartments'])}\n\n")
        
        f.write("Reaction Classification:\n")
        f.write(f"- Exchange reactions: {classification_stats['exchange_reactions']}\n")
        f.write(f"- Transport reactions: {classification_stats['transport_reactions']}\n")
        f.write(f"- Biomass reactions: {classification_stats['biomass_reactions']}\n")
        f.write(f"- Maintenance reactions: {classification_stats['maintenance_reactions']}\n")
        f.write(f"- Internal reactions: {classification_stats['internal_reactions']}\n\n")
        
        f.write("Metabolic Pathway Distribution:\n")
        for pathway, count in pathway_data['sorted_pathways']:
            percentage = (count / pathway_data['total_reactions']) * 100
            f.write(f"- {pathway}: {count} reactions ({percentage:.1f}%)\n")
        
        f.write(f"\nTop Reaction Prefixes:\n")
        sorted_prefixes = sorted(classification_stats['reaction_prefixes'].items(), 
                               key=lambda x: x[1], reverse=True)
        for prefix, count in sorted_prefixes[:20]:
            f.write(f"- {prefix}: {count}\n")
        
        f.write(f"\nGlycolysis Pathway Key Reactions:\n")
        for rxn in core_pathways['glycolysis_reactions'][:10]:
            f.write(f"- {rxn.id}: {rxn.name}\n")
        
        f.write(f"\nTCA Cycle Key Reactions:\n")
        for rxn in core_pathways['tca_reactions'][:10]:
            f.write(f"- {rxn.id}: {rxn.name}\n")
        
        f.write(f"\nImportant Exchange Reactions:\n")
        for rxn in core_pathways['important_exchanges'][:15]:
            f.write(f"- {rxn.id}: {rxn.name}\n")
    
    print(f"Detailed report saved to: {report_file}")

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """
    Main function - Execute complete metabolic model analysis workflow
    """
    print("="*60)
    print(f"Metabolic Network Model Analyzer - {SLOT_MODEL_NAME}")
    print("="*60)
    
    # 1. Load model
    model = load_metabolic_model(SLOT_MODEL_PATH)
    if model is None:
        print("Error: Unable to load model, exiting program")
        return
    
    # 2. Analyze basic information
    basic_info = analyze_basic_info(model)
    
    # 3. Reaction classification analysis
    classification_stats = analyze_reaction_classification(model)
    
    # 4. Metabolic pathway distribution analysis
    pathway_data = analyze_pathway_distribution(model, SLOT_CUSTOM_PATHWAYS)
    
    # 5. Core pathway detailed analysis
    core_pathways = analyze_core_pathways(model)
    
    # 6. Create output directory
    os.makedirs(SLOT_OUTPUT_DIR, exist_ok=True)
    
    # 7. Generate visualization charts
    if SLOT_GENERATE_VISUALIZATIONS:
        create_visualizations(model, basic_info, classification_stats, pathway_data, SLOT_OUTPUT_DIR)
    
    # 8. Generate detailed report
    if SLOT_SAVE_REPORT:
        generate_report(model, basic_info, classification_stats, pathway_data, core_pathways, SLOT_OUTPUT_DIR)
    
    print("\n" + "="*60)
    print("✓ Analysis completed!")
    print(f"Results saved in: {SLOT_OUTPUT_DIR}")
    print("="*60)

# =============================================================================
# PROGRAM ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
