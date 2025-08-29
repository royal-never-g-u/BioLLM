#!/usr/bin/env python3
"""
Constraint-Based Analysis Template
A comprehensive template for performing constraint-based metabolic analysis using COBRApy.

This template includes slots for:
- Model file path (provided by agent or uses default)
- Analysis parameters (growth rate thresholds, carbon sources, etc.)
- Output directory
- Analysis options (which analyses to perform)

Usage:
    python constraint_based_analysis_template.py
"""

import cobra
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from pathlib import Path

# =============================================================================
# SLOT DEFINITIONS - These will be filled by the agent
# =============================================================================

# SLOT: model_file_path
# Description: Path to the metabolic model file (SBML, JSON, or MAT format)
# Default: Uses a default E. coli model if not provided
MODEL_FILE_PATH = "{{model_file_path}}"  # Agent can provide: "path/to/model.xml"

# SLOT: output_directory
# Description: Directory to save analysis results and visualizations
# Default: Creates a timestamped directory
OUTPUT_DIRECTORY = "{{output_directory}}"  # Agent can provide: "results/analysis_2024"

# SLOT: analysis_parameters
# Description: Parameters for various analyses
ANALYSIS_PARAMETERS = {
    # Growth rate threshold for essentiality analysis (fraction of wild-type)
    "essentiality_threshold": {{essentiality_threshold}},  # Agent can provide: 0.01
    
    # Carbon sources to test for growth capability
    "carbon_sources": {{carbon_sources}},  # Agent can provide: ["glucose", "fructose", "acetate"]
    
    # Carbon source exchange reaction mapping
    "carbon_exchange_mapping": {{carbon_exchange_mapping}},  # Agent can provide: {"glucose": "EX_glc__D_e"}
    
    # Environmental conditions to test
    "environmental_conditions": {{environmental_conditions}},  # Agent can provide: ["pH", "temperature", "osmotic"]
    
    # pH conditions to test
    "ph_conditions": {{ph_conditions}},  # Agent can provide: {"Acidic": 10.0, "Neutral": 0.0, "Basic": -10.0}
    
    # Temperature conditions to test
    "temperature_conditions": {{temperature_conditions}},  # Agent can provide: {"Low": 5.0, "Optimal": 8.39, "High": 15.0}
    
    # Central metabolism reactions to test for essentiality
    "central_reactions": {{central_reactions}},  # Agent can provide: ["PGI", "PFK", "FBA", "TPI"]
    
    # Analysis options (which analyses to perform)
    "perform_basic_info": {{perform_basic_info}},  # Agent can provide: True
    "perform_fba": {{perform_fba}},  # Agent can provide: True
    "perform_growth_analysis": {{perform_growth_analysis}},  # Agent can provide: True
    "perform_environmental_analysis": {{perform_environmental_analysis}},  # Agent can provide: True
    "perform_essentiality_analysis": {{perform_essentiality_analysis}},  # Agent can provide: True
    "create_visualizations": {{create_visualizations}},  # Agent can provide: True
}

# SLOT: model_loading_options
# Description: Options for model loading and preprocessing
MODEL_LOADING_OPTIONS = {
    "model_format": {{model_format}},  # Agent can provide: "sbml", "json", "mat"
    "preprocess_model": {{preprocess_model}},  # Agent can provide: True
    "remove_blocked_reactions": {{remove_blocked_reactions}},  # Agent can provide: False
    "set_objective": {{set_objective}},  # Agent can provide: "BIOMASS_Ec_iML1515_core_75p37M"
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_model(model_path, options=None):
    """
    Load metabolic model with error handling and preprocessing.
    
    Args:
        model_path (str): Path to model file
        options (dict): Loading options
    
    Returns:
        cobra.Model: Loaded metabolic model
    """
    if options is None:
        options = {}
    
    print(f"=== Loading metabolic model from: {model_path} ===")
    
    try:
        # Determine model format and load accordingly
        model_format = options.get("model_format", "auto")
        
        if model_format == "auto":
            if model_path.endswith('.xml') or model_path.endswith('.sbml'):
                model_format = "sbml"
            elif model_path.endswith('.json'):
                model_format = "json"
            elif model_path.endswith('.mat'):
                model_format = "mat"
        
        if model_format == "sbml":
            model = cobra.io.read_sbml_model(model_path)
        elif model_format == "json":
            model = cobra.io.load_json_model(model_path)
        elif model_format == "mat":
            model = cobra.io.load_matlab_model(model_path)
        else:
            raise ValueError(f"Unsupported model format: {model_format}")
        
        print(f"✓ Model loaded successfully: {model.name}")
        
        # Apply preprocessing if requested
        if options.get("preprocess_model", False):
            print("Applying model preprocessing...")
            # Remove blocked reactions if requested
            if options.get("remove_blocked_reactions", False):
                blocked_reactions = cobra.flux_analysis.find_blocked_reactions(model)
                model.remove_reactions(blocked_reactions)
                print(f"Removed {len(blocked_reactions)} blocked reactions")
            
            # Set objective if specified
            objective = options.get("set_objective")
            if objective:
                if objective in model.reactions:
                    model.objective = objective
                    print(f"Set objective to: {objective}")
                else:
                    print(f"Warning: Objective reaction '{objective}' not found in model")
        
        return model
        
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Attempting to load default E. coli core model...")
        
        # Load default model as fallback
        try:
            model = cobra.io.load_model("e_coli_core")
            print("✓ Default E. coli core model loaded successfully")
            return model
        except Exception as e2:
            print(f"Error loading default model: {e2}")
            raise

def create_output_directory(output_dir):
    """
    Create output directory for results.
    
    Args:
        output_dir (str): Output directory path
    
    Returns:
        str: Created directory path
    """
    if not output_dir:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"constraint_analysis_results_{timestamp}"
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"✓ Output directory created: {output_dir}")
    return output_dir

def analyze_basic_info(model):
    """
    Analyze basic model information and structure.
    
    Args:
        model (cobra.Model): Metabolic model
    
    Returns:
        dict: Basic model information
    """
    print("\n=== Basic Model Information Analysis ===")
    
    info = {
        "name": model.name,
        "id": model.id,
        "reactions_count": len(model.reactions),
        "metabolites_count": len(model.metabolites),
        "genes_count": len(model.genes),
        "compartments": {},
        "objective": str(model.objective),
        "objective_direction": model.objective.direction,
        "exchange_reactions": [],
        "transport_reactions": [],
        "internal_reactions": []
    }
    
    print(f"Model name: {info['name']}")
    print(f"Model ID: {info['id']}")
    print(f"Number of reactions: {info['reactions_count']}")
    print(f"Number of metabolites: {info['metabolites_count']}")
    print(f"Number of genes: {info['genes_count']}")
    
    # Get compartments
    for compartment in model.compartments:
        info["compartments"][compartment] = model.compartments[compartment]
    
    print(f"\nCompartments:")
    for comp_id, comp_name in info["compartments"].items():
        print(f"  {comp_id}: {comp_name}")
    
    # Check objective function
    print(f"\nObjective function: {info['objective']}")
    print(f"Objective direction: {info['objective_direction']}")
    
    # Categorize reactions
    exchange_reactions = [r for r in model.reactions if r.id.startswith('EX_')]
    transport_reactions = [r for r in model.reactions if any(keyword in r.name.lower() 
                           for keyword in ['transport', 'transporter', 'symporter', 'antiporter']) 
                           if hasattr(r, 'name') and r.name]
    
    info["exchange_reactions"] = [r.id for r in exchange_reactions]
    info["transport_reactions"] = [r.id for r in transport_reactions]
    info["internal_reactions"] = [r.id for r in model.reactions 
                                 if r.id not in info["exchange_reactions"] 
                                 and r.id not in info["transport_reactions"]]
    
    print(f"\nReaction categories:")
    print(f"  Exchange reactions: {len(exchange_reactions)}")
    print(f"  Transport reactions: {len(transport_reactions)}")
    print(f"  Internal reactions: {len(info['internal_reactions'])}")
    
    print("✓ Basic model information analysis completed")
    return info

def perform_fba_analysis(model):
    """
    Perform basic Flux Balance Analysis.
    
    Args:
        model (cobra.Model): Metabolic model
    
    Returns:
        dict: FBA results
    """
    print("\n=== Basic Flux Balance Analysis ===")
    
    # Perform FBA
    solution = model.optimize()
    
    results = {
        "status": solution.status,
        "objective_value": solution.objective_value,
        "exchange_fluxes": {},
        "uptake_reactions": [],
        "secretion_reactions": []
    }
    
    print(f"FBA Solution Status: {results['status']}")
    print(f"Objective Value (Growth Rate): {results['objective_value']:.6f} h⁻¹")
    
    if solution.status == 'optimal':
        print(f"Model is feasible and optimal solution found")
        
        # Get flux distribution for exchange reactions
        exchange_reactions = [r for r in model.reactions if r.id.startswith('EX_')]
        exchange_fluxes = {}
        
        for reaction in exchange_reactions:
            flux = solution.fluxes[reaction.id]
            if abs(flux) > 1e-6:  # Only show non-zero fluxes
                exchange_fluxes[reaction.id] = flux
                results["exchange_fluxes"][reaction.id] = flux
        
        print(f"\nActive exchange reactions ({len(exchange_fluxes)} out of {len(exchange_reactions)}):")
        
        # Sort by flux magnitude
        sorted_fluxes = sorted(exchange_fluxes.items(), key=lambda x: abs(x[1]), reverse=True)
        
        print("Top 10 uptake reactions (negative flux):")
        uptake_count = 0
        for rxn_id, flux in sorted_fluxes:
            if flux < -1e-6 and uptake_count < 10:
                print(f"  {rxn_id}: {flux:.6f} mmol/gDW/h")
                results["uptake_reactions"].append({"reaction": rxn_id, "flux": flux})
                uptake_count += 1
        
        print("\nTop 10 secretion reactions (positive flux):")
        secretion_count = 0
        for rxn_id, flux in sorted_fluxes:
            if flux > 1e-6 and secretion_count < 10:
                print(f"  {rxn_id}: {flux:.6f} mmol/gDW/h")
                results["secretion_reactions"].append({"reaction": rxn_id, "flux": flux})
                secretion_count += 1
    else:
        print(f"Model optimization failed with status: {results['status']}")
    
    print("✓ Basic FBA completed")
    return results

def analyze_growth_capabilities(model, carbon_sources, carbon_exchange_mapping):
    """
    Analyze growth capabilities on different carbon sources and conditions.
    
    Args:
        model (cobra.Model): Metabolic model
        carbon_sources (list): List of carbon sources to test
        carbon_exchange_mapping (dict): Mapping of carbon source names to exchange reaction IDs
    
    Returns:
        dict: Growth analysis results
    """
    print("\n=== Growth Capabilities Analysis ===")
    
    results = {
        "carbon_source_growth": {},
        "aerobic_growth": 0.0,
        "anaerobic_growth": 0.0,
        "growth_reduction_anaerobic": 0.0
    }
    
    print("Testing growth on different carbon sources:")
    print("Carbon Source\tGrowth Rate (h⁻¹)\tStatus")
    print("-" * 45)
    
    for carbon_name in carbon_sources:
        exchange_id = carbon_exchange_mapping.get(carbon_name, f"EX_{carbon_name}_e")
        
        try:
            # Instead of copying the model, we'll modify the original and restore it
            # Store original bounds
            original_bounds = {}
            all_carbon_exchanges = list(carbon_exchange_mapping.values())
            
            # Store original bounds for all carbon exchanges
            for ex in all_carbon_exchanges:
                if ex in [r.id for r in model.reactions]:
                    reaction = model.reactions.get_by_id(ex)
                    original_bounds[ex] = (reaction.lower_bound, reaction.upper_bound)
                    reaction.lower_bound = 0  # Close all carbon source uptakes
            
            # Open the specific carbon source
            if exchange_id in [r.id for r in model.reactions]:
                reaction = model.reactions.get_by_id(exchange_id)
                reaction.lower_bound = -10.0
                
                # Optimize
                solution = model.optimize()
                growth_rate = solution.objective_value if solution.status == 'optimal' else 0.0
                results["carbon_source_growth"][carbon_name] = growth_rate
                
                print(f"{carbon_name:<12}\t{growth_rate:.6f}\t\t{solution.status}")
            else:
                results["carbon_source_growth"][carbon_name] = 0.0
                print(f"{carbon_name:<12}\t0.000000\t\tNot available")
            
            # Restore original bounds
            for ex, (lb, ub) in original_bounds.items():
                if ex in [r.id for r in model.reactions]:
                    reaction = model.reactions.get_by_id(ex)
                    reaction.lower_bound = lb
                    reaction.upper_bound = ub
                    
        except Exception as e:
            print(f"Error testing {carbon_name}: {e}")
            results["carbon_source_growth"][carbon_name] = 0.0
            print(f"{carbon_name:<12}\t0.000000\t\tError")
    
    # Test aerobic vs anaerobic conditions
    print(f"\n=== Aerobic vs Anaerobic Growth Comparison ===")
    
    try:
        # Aerobic conditions (default)
        aerobic_solution = model.optimize()
        results["aerobic_growth"] = aerobic_solution.objective_value if aerobic_solution.status == 'optimal' else 0.0
        
        # Anaerobic conditions
        if 'EX_o2_e' in [r.id for r in model.reactions]:
            # Store original oxygen bounds
            o2_reaction = model.reactions.get_by_id('EX_o2_e')
            original_o2_bounds = (o2_reaction.lower_bound, o2_reaction.upper_bound)
            
            # Set no oxygen uptake
            o2_reaction.lower_bound = 0
            o2_reaction.upper_bound = 0
            
            anaerobic_solution = model.optimize()
            results["anaerobic_growth"] = anaerobic_solution.objective_value if anaerobic_solution.status == 'optimal' else 0.0
            
            # Restore original oxygen bounds
            o2_reaction.lower_bound = original_o2_bounds[0]
            o2_reaction.upper_bound = original_o2_bounds[1]
        else:
            results["anaerobic_growth"] = results["aerobic_growth"]  # No oxygen reaction found
        
        print(f"Aerobic growth rate: {results['aerobic_growth']:.6f} h⁻¹")
        print(f"Anaerobic growth rate: {results['anaerobic_growth']:.6f} h⁻¹")
        
        if results["aerobic_growth"] > 0:
            results["growth_reduction_anaerobic"] = ((results["aerobic_growth"] - results["anaerobic_growth"]) / results["aerobic_growth"] * 100)
            print(f"Growth reduction under anaerobic conditions: {results['growth_reduction_anaerobic']:.1f}%")
        else:
            print("Cannot calculate growth reduction - aerobic growth is zero")
            
    except Exception as e:
        print(f"Error in aerobic/anaerobic analysis: {e}")
        results["aerobic_growth"] = 0.0
        results["anaerobic_growth"] = 0.0
        results["growth_reduction_anaerobic"] = 0.0
    
    print("✓ Growth capabilities analysis completed")
    return results

def analyze_environmental_conditions(model, ph_conditions, temperature_conditions):
    """
    Analyze model behavior under different environmental conditions.
    
    Args:
        model (cobra.Model): Metabolic model
        ph_conditions (dict): pH conditions to test
        temperature_conditions (dict): Temperature conditions to test
    
    Returns:
        dict: Environmental analysis results
    """
    print("\n=== Environmental Conditions Analysis ===")
    
    results = {
        "ph_analysis": {},
        "temperature_analysis": {},
        "osmotic_analysis": {}
    }
    
    # Test pH conditions
    print("Testing pH sensitivity through proton exchange analysis...")
    print("pH Condition\tProton Exchange\tGrowth Rate\tStatus")
    print("-" * 55)
    
    for ph_name, h_bound in ph_conditions.items():
        try:
            # Store original proton bounds
            original_h_bounds = None
            if 'EX_h_e' in [r.id for r in model.reactions]:
                h_reaction = model.reactions.get_by_id('EX_h_e')
                original_h_bounds = (h_reaction.lower_bound, h_reaction.upper_bound)
                
                # Adjust proton exchange bounds
                if h_bound > 0:  # Acidic - allow more proton uptake
                    h_reaction.lower_bound = -h_bound
                elif h_bound < 0:  # Basic - force proton secretion
                    h_reaction.upper_bound = -h_bound
                    h_reaction.lower_bound = -h_bound
            
            solution = model.optimize()
            growth_rate = solution.objective_value if solution.status == 'optimal' else 0.0
            
            results["ph_analysis"][ph_name] = {
                "proton_exchange": h_bound,
                "growth_rate": growth_rate,
                "status": solution.status
            }
            
            print(f"{ph_name:<15}\t{h_bound:>8.1f}\t\t{growth_rate:.6f}\t{solution.status}")
            
            # Restore original proton bounds
            if original_h_bounds and 'EX_h_e' in [r.id for r in model.reactions]:
                h_reaction = model.reactions.get_by_id('EX_h_e')
                h_reaction.lower_bound = original_h_bounds[0]
                h_reaction.upper_bound = original_h_bounds[1]
                
        except Exception as e:
            print(f"Error testing pH condition {ph_name}: {e}")
            results["ph_analysis"][ph_name] = {
                "proton_exchange": h_bound,
                "growth_rate": 0.0,
                "status": "error"
            }
    
    # Test temperature conditions (simulated through ATP maintenance)
    print(f"\nTesting temperature sensitivity through ATP maintenance...")
    print("Temperature\tATP Maintenance\tGrowth Rate\tStatus")
    print("-" * 50)
    
    # Get original ATP maintenance
    original_atp_maintenance = None
    if 'ATPM' in [r.id for r in model.reactions]:
        atpm_reaction = model.reactions.get_by_id('ATPM')
        original_atp_maintenance = atpm_reaction.lower_bound
    
    for temp_name, atp_maintenance in temperature_conditions.items():
        try:
            if 'ATPM' in [r.id for r in model.reactions]:
                atpm_reaction = model.reactions.get_by_id('ATPM')
                atpm_reaction.lower_bound = atp_maintenance
            
            solution = model.optimize()
            growth_rate = solution.objective_value if solution.status == 'optimal' else 0.0
            
            results["temperature_analysis"][temp_name] = {
                "atp_maintenance": atp_maintenance,
                "growth_rate": growth_rate,
                "status": solution.status
            }
            
            print(f"{temp_name:<12}\t{atp_maintenance:>8.1f}\t\t{growth_rate:.6f}\t{solution.status}")
            
        except Exception as e:
            print(f"Error testing temperature condition {temp_name}: {e}")
            results["temperature_analysis"][temp_name] = {
                "atp_maintenance": atp_maintenance,
                "growth_rate": 0.0,
                "status": "error"
            }
    
    # Restore original ATP maintenance
    if original_atp_maintenance is not None and 'ATPM' in [r.id for r in model.reactions]:
        atpm_reaction = model.reactions.get_by_id('ATPM')
        atpm_reaction.lower_bound = original_atp_maintenance
    
    print("✓ Environmental conditions analysis completed")
    return results

def analyze_essential_reactions(model, central_reactions, essentiality_threshold):
    """
    Analyze essential reactions in central metabolism.
    
    Args:
        model (cobra.Model): Metabolic model
        central_reactions (list): List of central metabolism reactions to test
        essentiality_threshold (float): Growth threshold for essentiality
    
    Returns:
        dict: Essentiality analysis results
    """
    print("\n=== Essential Reactions Analysis ===")
    
    results = {
        "essential_reactions": [],
        "reaction_analysis": {},
        "total_tested": 0
    }
    
    # Filter to existing reactions
    existing_central_rxns = [rxn_id for rxn_id in central_reactions 
                           if rxn_id in [r.id for r in model.reactions]]
    
    results["total_tested"] = len(existing_central_rxns)
    
    print(f"Testing {len(existing_central_rxns)} central metabolism reactions for essentiality...")
    print("Reaction\tWild-type flux\tKnockout growth\tEssential?")
    print("-" * 60)
    
    # Get wild-type fluxes first
    wt_solution = model.optimize()
    wt_growth = wt_solution.objective_value
    
    for rxn_id in existing_central_rxns:
        # Get wild-type flux
        wt_flux = wt_solution.fluxes[rxn_id] if wt_solution.status == 'optimal' else 0.0
        
        # Test reaction knockout
        with model:
            rxn = model.reactions.get_by_id(rxn_id)
            rxn.knock_out()
            
            ko_solution = model.optimize()
            ko_growth = ko_solution.objective_value if ko_solution.status == 'optimal' else 0.0
            
            # Consider essential if growth drops below threshold
            is_essential = (ko_growth / wt_growth) < essentiality_threshold if wt_growth > 0 else ko_growth == 0
            
            if is_essential:
                results["essential_reactions"].append(rxn_id)
            
            results["reaction_analysis"][rxn_id] = {
                "wild_type_flux": wt_flux,
                "knockout_growth": ko_growth,
                "is_essential": is_essential
            }
            
            print(f"{rxn_id:<12}\t{wt_flux:>10.6f}\t{ko_growth:>12.6f}\t{'Yes' if is_essential else 'No'}")
    
    print(f"\nFound {len(results['essential_reactions'])} essential reactions in central metabolism:")
    for rxn_id in results["essential_reactions"]:
        reaction = model.reactions.get_by_id(rxn_id)
        print(f"  {rxn_id}: {reaction.name}")
    
    print("✓ Essential reactions analysis completed")
    return results

def create_visualizations(results, output_dir):
    """
    Create comprehensive visualizations of analysis results.
    
    Args:
        results (dict): Analysis results
        output_dir (str): Output directory
    """
    print("\n=== Creating Visualizations ===")
    
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Metabolic Model: Constraint-Based Analysis Results', fontsize=16, fontweight='bold')
    
    # Plot 1: Growth rates on different carbon sources
    if "growth_analysis" in results and "carbon_source_growth" in results["growth_analysis"]:
        ax1 = axes[0, 0]
        carbon_data = results["growth_analysis"]["carbon_source_growth"]
        carbon_names = list(carbon_data.keys())
        growth_rates = list(carbon_data.values())
        
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
    if "growth_analysis" in results:
        ax2 = axes[0, 1]
        conditions = ['Aerobic', 'Anaerobic']
        growth_vals = [results["growth_analysis"]["aerobic_growth"], 
                      results["growth_analysis"]["anaerobic_growth"]]
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
    if "environmental_analysis" in results and "temperature_analysis" in results["environmental_analysis"]:
        ax3 = axes[1, 0]
        temp_data = results["environmental_analysis"]["temperature_analysis"]
        temp_names = list(temp_data.keys())
        temp_growth = [temp_data[name]["growth_rate"] for name in temp_names]
        
        bars3 = ax3.bar(temp_names, temp_growth, color='orange', alpha=0.7)
        ax3.set_title('Temperature Effects on Growth', fontweight='bold')
        ax3.set_ylabel('Growth Rate (h⁻¹)')
        ax3.set_xlabel('Temperature')
        
        # Add value labels
        for bar, val in zip(bars3, temp_growth):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                     f'{val:.3f}', ha='center', va='bottom', fontsize=10)
    
    # Plot 4: pH sensitivity
    if "environmental_analysis" in results and "ph_analysis" in results["environmental_analysis"]:
        ax4 = axes[1, 1]
        ph_data = results["environmental_analysis"]["ph_analysis"]
        ph_names = list(ph_data.keys())
        ph_growth = [ph_data[name]["growth_rate"] for name in ph_names]
        
        bars4 = ax4.bar(ph_names, ph_growth, color='green', alpha=0.7)
        ax4.set_title('pH Effects on Growth', fontweight='bold')
        ax4.set_ylabel('Growth Rate (h⁻¹)')
        ax4.set_xlabel('pH Condition')
        
        # Add value labels
        for bar, val in zip(bars4, ph_growth):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                     f'{val:.3f}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    # Save the figure
    fig_path = os.path.join(output_dir, 'constraint_based_analysis.png')
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Visualization saved to: {fig_path}")
    print("✓ Visualizations created")

def save_results(results, output_dir):
    """
    Save analysis results to files.
    
    Args:
        results (dict): Analysis results
        output_dir (str): Output directory
    """
    print("\n=== Saving Results ===")
    
    # Save results as JSON
    results_file = os.path.join(output_dir, 'analysis_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"Results saved to: {results_file}")
    
    # Create summary report
    report_file = os.path.join(output_dir, 'analysis_summary.txt')
    with open(report_file, 'w') as f:
        f.write("CONSTRAINT-BASED ANALYSIS SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        
        if "basic_info" in results:
            f.write("MODEL INFORMATION:\n")
            f.write(f"  Name: {results['basic_info']['name']}\n")
            f.write(f"  Reactions: {results['basic_info']['reactions_count']}\n")
            f.write(f"  Metabolites: {results['basic_info']['metabolites_count']}\n")
            f.write(f"  Genes: {results['basic_info']['genes_count']}\n\n")
        
        if "fba_analysis" in results:
            f.write("FBA RESULTS:\n")
            f.write(f"  Growth Rate: {results['fba_analysis']['objective_value']:.6f} h⁻¹\n")
            f.write(f"  Status: {results['fba_analysis']['status']}\n\n")
        
        if "growth_analysis" in results:
            f.write("GROWTH CAPABILITIES:\n")
            f.write(f"  Aerobic Growth: {results['growth_analysis']['aerobic_growth']:.6f} h⁻¹\n")
            f.write(f"  Anaerobic Growth: {results['growth_analysis']['anaerobic_growth']:.6f} h⁻¹\n")
            f.write(f"  Growth Reduction (Anaerobic): {results['growth_analysis']['growth_reduction_anaerobic']:.1f}%\n\n")
        
        if "essentiality_analysis" in results:
            f.write("ESSENTIAL REACTIONS:\n")
            f.write(f"  Total Tested: {results['essentiality_analysis']['total_tested']}\n")
            f.write(f"  Essential Found: {len(results['essentiality_analysis']['essential_reactions'])}\n")
            for rxn_id in results['essentiality_analysis']['essential_reactions']:
                f.write(f"    - {rxn_id}\n")
    
    print(f"Summary report saved to: {report_file}")
    print("✓ Results saved")

# =============================================================================
# MAIN ANALYSIS FUNCTION
# =============================================================================

def run_constraint_based_analysis():
    """
    Main function to run the complete constraint-based analysis.
    """
    print("CONSTRAINT-BASED ANALYSIS TEMPLATE")
    print("=" * 50)
    
    # Initialize results dictionary
    results = {}
    
    # Create output directory
    output_dir = create_output_directory(OUTPUT_DIRECTORY)
    
    # Load model
    model = load_model(MODEL_FILE_PATH, MODEL_LOADING_OPTIONS)
    
    # Run analyses based on configuration
    if ANALYSIS_PARAMETERS.get("perform_basic_info", True):
        results["basic_info"] = analyze_basic_info(model)
    
    if ANALYSIS_PARAMETERS.get("perform_fba", True):
        results["fba_analysis"] = perform_fba_analysis(model)
    
    if ANALYSIS_PARAMETERS.get("perform_growth_analysis", True):
        carbon_sources = ANALYSIS_PARAMETERS.get("carbon_sources", ["glucose", "fructose", "acetate"])
        carbon_exchange_mapping = ANALYSIS_PARAMETERS.get("carbon_exchange_mapping", {
            "glucose": "EX_glc__D_e",
            "fructose": "EX_fru_e",
            "acetate": "EX_ac_e",
            "succinate": "EX_succ_e",
            "lactate": "EX_lac__L_e",
            "glycerol": "EX_glyc_e",
            "pyruvate": "EX_pyr_e"
        })
        results["growth_analysis"] = analyze_growth_capabilities(model, carbon_sources, carbon_exchange_mapping)
    
    if ANALYSIS_PARAMETERS.get("perform_environmental_analysis", True):
        ph_conditions = ANALYSIS_PARAMETERS.get("ph_conditions", {
            "Acidic": 10.0,
            "Neutral": 0.0,
            "Basic": -10.0
        })
        temperature_conditions = ANALYSIS_PARAMETERS.get("temperature_conditions", {
            "Low": 5.0,
            "Optimal": 8.39,
            "High": 15.0
        })
        results["environmental_analysis"] = analyze_environmental_conditions(model, ph_conditions, temperature_conditions)
    
    if ANALYSIS_PARAMETERS.get("perform_essentiality_analysis", True):
        central_reactions = ANALYSIS_PARAMETERS.get("central_reactions", [
            "PGI", "PFK", "FBA", "TPI", "GAPD", "PGK", "PGM", "ENO", "PYK",
            "CS", "ACONT", "ICDHyr", "AKGDH", "SUCOAS", "SUCDi", "FUM", "MDH"
        ])
        essentiality_threshold = ANALYSIS_PARAMETERS.get("essentiality_threshold", 0.01)
        results["essentiality_analysis"] = analyze_essential_reactions(model, central_reactions, essentiality_threshold)
    
    # Create visualizations
    if ANALYSIS_PARAMETERS.get("create_visualizations", True):
        create_visualizations(results, output_dir)
    
    # Save results
    save_results(results, output_dir)
    
    # Final status
    print("\n=== ANALYSIS COMPLETED ===")
    print("✓ All requested analyses completed successfully")
    print(f"✓ Results saved to: {output_dir}")
    
    return results

# =============================================================================
# EXECUTION
# =============================================================================

if __name__ == "__main__":
    try:
        results = run_constraint_based_analysis()
        print("\nAnalysis completed successfully!")
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()
