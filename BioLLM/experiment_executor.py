#!/usr/bin/env python3
"""
Experiment Executor - Handles experiment execution after model analysis
"""

import os
import json
import sys
import traceback
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bio_task import get_current_task, update_current_task



def execute_gene_deletion(model_name: str, model_location: str) -> Dict[str, Any]:
    """
    Execute gene deletion analysis using the GeneDeletion template
    
    Args:
        model_name (str): Name of the model to experiment with
        model_location (str): Location of the model file
        
    Returns:
        Dict containing execution status and results
    """
    try:
        # Add timestamp and clear call indication
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "="*80)
        print(f"🔬 EXECUTE_GENE_DELETION METHOD CALLED")
        print(f"⏰ Timestamp: {timestamp}")
        print(f"🎯 Model: {model_name}")
        print(f"📁 Location: {model_location}")
        print(f"🔄 Status: Starting gene deletion analysis...")
        print("="*80)
        
        print(f"🚀 Starting gene deletion analysis for model: {model_name}")
        print(f"📁 Model location: {model_location}")
        
        # Verify model file exists
        if not os.path.exists(model_location):
            return {
                'success': False,
                'error': f"Model file not found: {model_location}",
                'model_name': model_name,
                'model_location': model_location
            }
        
        # Note: We don't update task_type during execution to preserve user's analysis type
        # Only TaskPickAgent should update task_type when matching analysis types
        
        # Read bio_task content and create configuration override
        config_override = create_config_from_bio_task(model_name, model_location)
        
        # Execute gene deletion analysis using the template
        analysis_results = execute_gene_deletion_analysis(config_override)
        
        # Save analysis results
        results_file = save_analysis_results(analysis_results, model_name)
        
        # Note: We don't update task_type after completion to preserve user's analysis type
        # Only TaskPickAgent should update task_type when matching analysis types
        
        # Add completion timestamp
        completion_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"✅ Gene deletion analysis completed for {model_name}")
        print(f"📄 Results saved to: {results_file}")
        
        print("="*80)
        print(f"🎉 EXECUTE_GENE_DELETION METHOD COMPLETED SUCCESSFULLY")
        print(f"⏰ Completion Time: {completion_timestamp}")
        print(f"📊 Results: Analysis completed and saved")
        print("="*80 + "\n")
        
        # Extract visualization file paths from the collected visualizations
        visualization_paths = []
        if analysis_results.get('visualizations'):
            for viz in analysis_results['visualizations']:
                if isinstance(viz, dict) and 'path' in viz:
                    visualization_paths.append(viz['path'])
                elif isinstance(viz, str):
                    visualization_paths.append(viz)
        
        return {
            'success': True,
            'results': analysis_results,
            'results_file': results_file,
            'model_name': model_name,
            'model_location': model_location,
            'visualizations': visualization_paths,
            'reports': analysis_results.get('reports', [])
        }
        
    except Exception as e:
        # Add error timestamp
        error_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        error_result = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc(),
            'model_name': model_name,
            'model_location': model_location
        }
        
        print(f"❌ Error in gene deletion analysis: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        
        print("="*80)
        print(f"💥 EXECUTE_GENE_DELETION METHOD FAILED")
        print(f"⏰ Error Time: {error_timestamp}")
        print(f"❌ Error: {str(e)}")
        print("="*80 + "\n")
        
        # Note: We don't update task_type on error to preserve user's analysis type
        # Only TaskPickAgent should update task_type when matching analysis types
        
        return error_result

def create_config_from_bio_task(model_name: str, model_location: str) -> Dict[str, Any]:
    """
    Create configuration override from bio_task content
    
    Args:
        model_name (str): Name of the model
        model_location (str): Location of the model file
        
    Returns:
        Dict containing configuration override
    """
    try:
        # Read current bio_task
        current_task = get_current_task()
        
        # Create configuration override based on bio_task and model information
        config_override = {
            'model_config': {
                'model_name': model_name,
                'model_type': 'cobra',  # Default to cobra, can be customized
                'load_method': 'load_model',
                'model_description': f'Gene deletion analysis for {model_name}'
            },
            'analysis_scope': {
                'max_genes_to_analyze': 500,  # Default value, can be customized
                'gene_selection_strategy': 'representative',
                'focus_pathways': [
                    'glycolysis',
                    'tca_cycle', 
                    'fermentation',
                    'amino_acid_metabolism'
                ],
                'exclude_essential_genes': True,
                'min_growth_rate_threshold': 0.1
            },
            'target_products': {
                'EX_succ_e': {
                    'name': '琥珀酸 (Succinate)',
                    'priority': 1,
                    'target_improvement': 10.0,
                    'min_production_rate': 5.0
                },
                'EX_lac__L_e': {
                    'name': 'L-乳酸 (L-Lactate)', 
                    'priority': 2,
                    'target_improvement': 15.0,
                    'min_production_rate': 10.0
                },
                'EX_ac_e': {
                    'name': '醋酸 (Acetate)',
                    'priority': 3, 
                    'target_improvement': 20.0,
                    'min_production_rate': 15.0
                },
                'EX_etoh_e': {
                    'name': '乙醇 (Ethanol)',
                    'priority': 4,
                    'target_improvement': 25.0,
                    'min_production_rate': 12.0
                },
                'EX_for_e': {
                    'name': '甲酸 (Formate)',
                    'priority': 5,
                    'target_improvement': 30.0,
                    'min_production_rate': 50.0
                },
                'EX_pyr_e': {
                    'name': '丙酮酸 (Pyruvate)',
                    'priority': 6,
                    'target_improvement': 18.0,
                    'min_production_rate': 8.0
                }
            },
            'output_config': {
                'output_directory': f'Temp/gene_deletion_results_{model_name}',
                'file_prefix': f'gene_deletion_{model_name}',
                'include_timestamp': True,
                'create_subdirectories': True
            },
            'report_config': {
                'generate_summary_report': True,
                'generate_detailed_report': True,
                'generate_csv_results': True,
                'generate_json_results': True,
                'include_model_info': True,
                'include_methodology': True,
                'include_recommendations': True
            },
            'visualization_config': {
                'chart_types': {
                    'product_comparison': True,
                    'knockout_effects': True,
                    'gene_targets': True,
                    'growth_production_tradeoff': True,
                    'pathway_analysis': False
                }
            }
        }
        
        # If bio_task has specific configuration, merge it
        if current_task:
            task_dict = current_task.to_dict()
            if task_dict.get('task_type'):
                # Customize based on task type
                if task_dict['task_type'] == 'experiment':
                    config_override['analysis_scope']['max_genes_to_analyze'] = 1000
                elif task_dict['task_type'] == 'quick_analysis':
                    config_override['analysis_scope']['max_genes_to_analyze'] = 100
        
        return config_override
        
    except Exception as e:
        print(f"❌ Error creating configuration from bio_task: {e}")
        # Return default configuration
        return {
            'model_config': {
                'model_name': model_name,
                'model_type': 'cobra',
                'load_method': 'load_model',
                'model_description': f'Gene deletion analysis for {model_name}'
            }
        }

def execute_gene_deletion_analysis(config_override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute gene deletion analysis using the template
    
    Args:
        config_override (Dict): Configuration override for the analysis
        
    Returns:
        Dict containing analysis results
    """
    try:
        # Import the main template
        from CodeTemplate.GeneDeletion.main_template import GeneDeletionAnalysisTemplate
        
        print("📋 Initializing Gene Deletion Analysis Template...")
        
        # Create analyzer instance with configuration override
        analyzer = GeneDeletionAnalysisTemplate(config_override)
        
        print("🔬 Running complete gene deletion analysis...")
        
        # Run the complete analysis
        results = analyzer.run_complete_analysis()
        
        # Get analysis summary
        summary = analyzer.get_analysis_summary()
        
        # Get report paths
        report_paths = analyzer.report_generator.get_report_paths() if analyzer.report_generator else {}
        
        # Collect visualization files
        visualizations = collect_visualization_files(config_override.get('output_config', {}).get('output_directory', ''))
        
        # Compile comprehensive results
        analysis_results = {
            'analysis_completed': True,
            'summary': summary,
            'results': results,
            'report_paths': report_paths,
            'visualizations': visualizations,
            'config_used': config_override
        }
        
        print("✅ Gene deletion analysis completed successfully")
        
        return analysis_results
        
    except Exception as e:
        print(f"❌ Error executing gene deletion analysis: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise

def collect_visualization_files(output_directory: str) -> List[Dict[str, str]]:
    """
    Collect visualization files from output directory
    
    Args:
        output_directory (str): Output directory path
        
    Returns:
        List of visualization file information
    """
    visualizations = []
    
    try:
        if not os.path.exists(output_directory):
            return visualizations
        
        # Look for image files
        image_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.pdf']
        for file in os.listdir(output_directory):
            file_path = os.path.join(output_directory, file)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in image_extensions:
                    visualizations.append({
                        'name': file,
                        'path': file_path,
                        'type': 'image',
                        'size': os.path.getsize(file_path)
                    })
        
        # Look for HTML files
        for file in os.listdir(output_directory):
            file_path = os.path.join(output_directory, file)
            if os.path.isfile(file_path) and file.endswith('.html'):
                visualizations.append({
                    'name': file,
                    'path': file_path,
                    'type': 'html',
                    'size': os.path.getsize(file_path)
                })
        
        print(f"📊 Found {len(visualizations)} visualization files")
        
    except Exception as e:
        print(f"❌ Error collecting visualization files: {e}")
    
    return visualizations

def save_analysis_results(analysis_results: Dict[str, Any], model_name: str) -> str:
    """
    Save analysis results to file
    
    Args:
        analysis_results (Dict): Analysis results to save
        model_name (str): Name of the model
        
    Returns:
        str: Path to the saved results file
    """
    try:
        # Create results directory
        temp_dir = "Temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save comprehensive results
        results_file = os.path.join(temp_dir, f"gene_deletion_results_{model_name}.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False, default=str)
        
        # Save summary separately
        summary_file = os.path.join(temp_dir, f"gene_deletion_summary_{model_name}.json")
        if 'summary' in analysis_results:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_results['summary'], f, indent=2, ensure_ascii=False, default=str)
        
        print(f"💾 Analysis results saved to: {results_file}")
        print(f"📋 Summary saved to: {summary_file}")
        
        return results_file
        
    except Exception as e:
        print(f"❌ Error saving analysis results: {e}")
        return ""

def get_analysis_status(model_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the status of gene deletion analysis for a specific model
    
    Args:
        model_name (str): Name of the model
        
    Returns:
        Dict containing analysis status or None if not found
    """
    try:
        temp_dir = "Temp"
        results_file = os.path.join(temp_dir, f"gene_deletion_results_{model_name}.json")
        
        if os.path.exists(results_file):
            with open(results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error getting analysis status: {e}")
        return None

def list_gene_deletion_analyses() -> List[Dict[str, Any]]:
    """
    List all available gene deletion analyses
    
    Returns:
        List of analysis information
    """
    try:
        temp_dir = "Temp"
        analyses = []
        
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                if file.startswith("gene_deletion_results_") and file.endswith(".json"):
                    model_name = file.replace("gene_deletion_results_", "").replace(".json", "")
                    analysis_data = get_analysis_status(model_name)
                    if analysis_data:
                        analyses.append(analysis_data)
        
        return analyses
        
    except Exception as e:
        print(f"❌ Error listing gene deletion analyses: {e}")
        return []

def clear_analysis_results(model_name: str = None) -> bool:
    """
    Clear gene deletion analysis results
    
    Args:
        model_name (str): Specific model to clear, or None to clear all
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        temp_dir = "Temp"
        
        if model_name:
            # Clear specific model
            results_file = os.path.join(temp_dir, f"gene_deletion_results_{model_name}.json")
            summary_file = os.path.join(temp_dir, f"gene_deletion_summary_{model_name}.json")
            
            cleared = False
            if os.path.exists(results_file):
                os.remove(results_file)
                cleared = True
            if os.path.exists(summary_file):
                os.remove(summary_file)
                cleared = True
            
            if cleared:
                print(f"✅ Cleared analysis results for {model_name}")
                return True
            else:
                print(f"⚠️ No analysis results found for {model_name}")
                return False
        else:
            # Clear all analyses
            cleared_count = 0
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    if file.startswith("gene_deletion_results_") and file.endswith(".json"):
                        os.remove(os.path.join(temp_dir, file))
                        cleared_count += 1
                    elif file.startswith("gene_deletion_summary_") and file.endswith(".json"):
                        os.remove(os.path.join(temp_dir, file))
                        cleared_count += 1
            
            print(f"✅ Cleared {cleared_count} analysis result files")
            return True
            
    except Exception as e:
        print(f"❌ Error clearing analysis results: {e}")
        return False

def get_analysis_visualizations(model_name: str) -> List[Dict[str, str]]:
    """
    Get visualization files for a specific model analysis
    
    Args:
        model_name (str): Name of the model
        
    Returns:
        List of visualization file information
    """
    try:
        analysis_data = get_analysis_status(model_name)
        if analysis_data and 'visualizations' in analysis_data:
            return analysis_data['visualizations']
        else:
            return []
            
    except Exception as e:
        print(f"❌ Error getting analysis visualizations: {e}")
        return []

def get_analysis_reports(model_name: str) -> List[Dict[str, str]]:
    """
    Get report files for a specific model analysis
    
    Args:
        model_name (str): Name of the model
        
    Returns:
        List of report file information
    """
    try:
        analysis_data = get_analysis_status(model_name)
        if analysis_data and 'report_paths' in analysis_data:
            reports = []
            for report_type, report_path in analysis_data['report_paths'].items():
                if os.path.exists(report_path):
                    reports.append({
                        'type': report_type,
                        'path': report_path,
                        'name': os.path.basename(report_path)
                    })
            return reports
        else:
            return []
            
    except Exception as e:
        print(f"❌ Error getting analysis reports: {e}")
        return []

def execute_experiment(model_name: str = None, task_type: int = None) -> Dict[str, Any]:
    """
    Execute experiment based on model and task type
    
    Args:
        model_name (str, optional): Name of the model. If None, reads from bio_task
        task_type (int, optional): Type of analysis task. If None, reads from bio_task
        
    Returns:
        Dict containing execution status and results
    """
    try:
        # Add timestamp and clear call indication
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "="*80)
        print(f"🔬 EXECUTE_EXPERIMENT METHOD CALLED")
        print(f"⏰ Timestamp: {timestamp}")
        print(f"🎯 Model: {model_name}")
        print(f"📋 Task Type: {task_type}")
        print(f"🔄 Status: Starting experiment execution...")
        print("="*80)
        
        # Get current task if parameters not provided
        if model_name is None or task_type is None:
            try:
                from bio_task import get_current_task
                current_task = get_current_task()
                model_name = model_name or current_task.model_name
                task_type = task_type or current_task.task_type
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Failed to read bio_task: {str(e)}',
                    'model_name': model_name,
                    'task_type': task_type
                }
        
        # Validate parameters after potentially reading from bio_task
        if not model_name or not model_name.strip():
            return {
                'success': False,
                'error': 'Model name is required',
                'model_name': model_name,
                'task_type': task_type
            }
        
        if task_type is None:
            return {
                'success': False,
                'error': 'Task type is required',
                'model_name': model_name,
                'task_type': task_type
            }
        
        # Get model location from bio_task or use default
        try:
            from bio_task import get_current_task
            current_task = get_current_task()
            model_location = current_task.model_local or f"../downloads/{model_name}.mat"
        except:
            model_location = f"../downloads/{model_name}.mat"  # Default location
        
        # Execute experiment based on task_type
        print(f"🔍 Executing analysis for task type {task_type}...")
        
        # Check if task_type is within agent's capabilities
        if task_type == 1:
            # Flux Balance Analysis (FBA)
            result = execute_fba(model_name, model_location)
        elif task_type == 2:
            # Gene Knockout Analysis
            result = execute_gene_deletion(model_name, model_location)
        elif task_type == 6:
            # Constraint-Based Analysis
            result = execute_constraint_based_analysis(model_name, model_location)
        else:
            # Task type not within agent's capabilities
            return {
                'success': False,
                'error': f'This part is not within the agent\'s capabilities. Task type {task_type} is not supported.',
                'model_name': model_name,
                'task_type': task_type,
                'model_location': model_location,
                'message': 'This part is not within the agent\'s capabilities. Please use task types 1 (FBA), 2 (Gene Deletion), or 6 (Constraint-Based Analysis).'
            }
        
        completion_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("="*80)
        print(f"🎉 EXECUTE_EXPERIMENT METHOD COMPLETED SUCCESSFULLY")
        print(f"⏰ Completion Time: {completion_timestamp}")
        print(f"📊 Results: {result.get('success', False)}")
        print("="*80 + "\n")
        
        # Add experiment metadata to result
        result['experiment_timestamp'] = timestamp
        result['experiment_completion_timestamp'] = completion_timestamp
        result['experiment_task_type'] = task_type
        
        return result
        
    except Exception as e:
        error_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_result = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc(),
            'model_name': model_name,
            'task_type': task_type
        }
        print("="*80)
        print(f"💥 EXECUTE_EXPERIMENT METHOD FAILED")
        print(f"⏰ Error Time: {error_timestamp}")
        print(f"❌ Error: {str(e)}")
        print("="*80 + "\n")
        return error_result


def execute_fba(model_name: str, model_location: str) -> Dict[str, Any]:
    """
    Execute FBA analysis using the FBA template
    
    Args:
        model_name (str): Name of the model to experiment with
        model_location (str): Location of the model file
        
    Returns:
        Dict containing execution status and results
    """
    try:
        # Add timestamp and clear call indication
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "="*80)
        print(f"🔬 EXECUTE_FBA METHOD CALLED")
        print(f"⏰ Timestamp: {timestamp}")
        print(f"🎯 Model: {model_name}")
        print(f"📁 Location: {model_location}")
        print(f"🔄 Status: Starting FBA analysis...")
        print("="*80)
        
        print(f"🚀 Starting FBA analysis for model: {model_name}")
        print(f"📁 Model location: {model_location}")
        
        # Verify model file exists
        if not os.path.exists(model_location):
            return {
                'success': False,
                'error': f"Model file not found: {model_location}",
                'model_name': model_name,
                'model_location': model_location
            }
        
        # Read bio_task content and create configuration override
        config_override = create_fba_config_from_bio_task(model_name, model_location)
        
        # Execute FBA analysis using the template
        analysis_results = execute_fba_analysis(config_override)
        
        # Save analysis results
        results_file = save_fba_analysis_results(analysis_results, model_name)
        
        # Generate comprehensive report using LLM
        report = generate_fba_analysis_report(analysis_results, model_name)
        
        # Add completion timestamp
        completion_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"✅ FBA analysis completed for {model_name}")
        print(f"📄 Results saved to: {results_file}")
        print(f"📋 Report generated: {len(report)} characters")
        
        print("="*80)
        print(f"🎉 EXECUTE_FBA METHOD COMPLETED SUCCESSFULLY")
        print(f"⏰ Completion Time: {completion_timestamp}")
        print(f"📊 Results: Analysis completed and saved")
        print("="*80 + "\n")
        
        # Extract visualization file paths from the collected visualizations
        visualization_paths = []
        if analysis_results.get('visualizations'):
            for viz in analysis_results['visualizations']:
                if isinstance(viz, dict) and 'path' in viz:
                    visualization_paths.append(viz['path'])
                elif isinstance(viz, str):
                    visualization_paths.append(viz)
        
        return {
            'success': True,
            'results': analysis_results,
            'results_file': results_file,
            'report': report,
            'model_name': model_name,
            'model_location': model_location,
            'task_type': 1,  # FBA Analysis
            'visualizations': visualization_paths,
            'reports': analysis_results.get('reports', [])
        }
        
    except Exception as e:
        # Add error timestamp
        error_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        error_result = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc(),
            'model_name': model_name,
            'model_location': model_location
        }
        
        print(f"❌ Error in FBA analysis: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        
        print("="*80)
        print(f"💥 EXECUTE_FBA METHOD FAILED")
        print(f"⏰ Error Time: {error_timestamp}")
        print(f"❌ Error: {str(e)}")
        print("="*80 + "\n")
        
        return error_result

def create_fba_config_from_bio_task(model_name: str, model_location: str) -> Dict[str, Any]:
    """
    Create FBA configuration from bio_task information
    
    Args:
        model_name (str): Name of the model
        model_location (str): Location of the model file
        
    Returns:
        Dict containing FBA configuration
    """
    try:
        # Get current bio_task
        current_task = get_current_task()
        
        # Create configuration override for FBA analysis
        config_override = {
            'model_config': {
                'model_name': model_name,
                'model_location': model_location,
                'model_url': f"http://bigg.ucsd.edu/static/models/{model_name}.xml.gz",
                'biomass_reaction_id': f"BIOMASS_Ec_{model_name}_core_75p37M"
            },
            'output_config': {
                'output_directory': f"/tmp/fba_analysis_{model_name}",
                'figure_size': (18, 12),
                'dpi': 300
            },
            'analysis_config': {
                'glucose_uptake_rates': [5, 10, 15, 20, 25],
                'oxygen_availability_rates': [10, 20, 30, 40, 50],
                'significant_flux_threshold': 0.001,
                'test_genes': ['b0008', 'b0114', 'b1136', 'b2925', 'b0720'],
                'key_reactions': [
                    f'BIOMASS_Ec_{model_name}_core_75p37M',
                    'EX_glc__D_e',
                    'EX_o2_e',
                    'EX_co2_e',
                    'EX_h2o_e',
                    'ATPS4rpp',
                    'CYTBO3_4pp'
                ]
            },
            'visualization_config': {
                'generate_plots': True,
                'save_plots': True,
                'plot_format': 'png'
            },
            'report_config': {
                'generate_csv_results': True,
                'generate_summary_report': True,
                'include_visualizations': True
            }
        }
        
        print(f"📋 Created FBA configuration for {model_name}")
        print(f"📁 Output directory: {config_override['output_config']['output_directory']}")
        print(f"🔬 Analysis parameters: {len(config_override['analysis_config']['glucose_uptake_rates'])} glucose rates, {len(config_override['analysis_config']['oxygen_availability_rates'])} oxygen rates")
        
        return config_override
        
    except Exception as e:
        print(f"❌ Error creating FBA configuration: {e}")
        raise

def execute_fba_analysis(config_override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute FBA analysis using the template
    
    Args:
        config_override (Dict): Configuration override for the analysis
        
    Returns:
        Dict containing analysis results
    """
    try:
        # Import the FBA template
        from CodeTemplate.FBA.simple_fba_template import main as fba_main
        
        print("📋 Initializing FBA Analysis Template...")
        
        # Create a temporary script with the configuration
        temp_script = create_fba_script_from_config(config_override)
        
        print("🔬 Running complete FBA analysis...")
        
        # Execute the FBA analysis
        results = execute_fba_script(temp_script, config_override)
        
        # Collect results from the actual output directory
        actual_output_dir = config_override.get('output_config', {}).get('output_directory', '/tmp/fba_analysis')
        collected_results = collect_fba_results(actual_output_dir)
        
        # Update results with collected data
        results['results'] = collected_results
        
        # Collect visualization files
        visualizations = collect_fba_visualization_files(actual_output_dir)
        
        # Generate analysis summary
        summary = generate_fba_analysis_summary(results, config_override)
        
        # Compile comprehensive results
        analysis_results = {
            'analysis_completed': True,
            'summary': summary,
            'results': results,
            'visualizations': visualizations,
            'config_used': config_override,
            'output_directory': config_override.get('output_config', {}).get('output_directory', '')
        }
        
        # Clean up temporary script
        if os.path.exists(temp_script):
            os.remove(temp_script)
        
        print("✅ FBA analysis completed successfully")
        
        return analysis_results
        
    except Exception as e:
        print(f"❌ Error executing FBA analysis: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise

def create_fba_script_from_config(config_override: Dict[str, Any]) -> str:
    """
    Create a custom FBA script from configuration
    
    Args:
        config_override (Dict): Configuration override
        
    Returns:
        str: Path to the temporary script
    """
    try:
        # Read the complete FBA template (with full functionality)
        template_path = "CodeTemplate/FBA/simple_fba_template.py"
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Extract configuration values
        model_config = config_override.get('model_config', {})
        output_config = config_override.get('output_config', {})
        analysis_config = config_override.get('analysis_config', {})
        
        # Replace slots with actual values
        custom_content = template_content.replace('{{MODEL_URL}}', model_config.get('model_url', ''))
        custom_content = custom_content.replace('{{MODEL_NAME}}', model_config.get('model_name', ''))
        custom_content = custom_content.replace('{{BIOMASS_REACTION_ID}}', model_config.get('biomass_reaction_id', ''))
        custom_content = custom_content.replace('"{{OUTPUT_DIR}}"', f'"{output_config.get("output_directory", "")}"')
        
        # Replace all slots for complete FBA template
        glucose_rates = analysis_config.get('glucose_uptake_rates', [5, 10, 15, 20, 25])
        oxygen_rates = analysis_config.get('oxygen_availability_rates', [10, 20, 30, 40, 50])
        flux_threshold = analysis_config.get('significant_flux_threshold', 0.001)
        test_genes = analysis_config.get('test_genes', ['b0008', 'b0114', 'b1136'])
        key_reactions = analysis_config.get('key_reactions', ['BIOMASS_Ec_iML1515_core_75p37M', 'EX_glc__D_e', 'EX_o2_e'])
        
        # Replace string slots with actual values (remove quotes)
        custom_content = custom_content.replace('"{{GLUCOSE_RATES}}"', str(glucose_rates))
        custom_content = custom_content.replace('"{{OXYGEN_RATES}}"', str(oxygen_rates))
        custom_content = custom_content.replace('"{{FLUX_THRESHOLD}}"', str(flux_threshold))
        custom_content = custom_content.replace('"{{TEST_GENES}}"', str(test_genes))
        custom_content = custom_content.replace('"{{KEY_REACTIONS}}"', str(key_reactions))
        
        # Write the custom script
        temp_script_path = f"Temp/temp_fba_{model_config.get('model_name', 'analysis')}.py"
        os.makedirs(os.path.dirname(temp_script_path), exist_ok=True)
        
        with open(temp_script_path, 'w') as f:
            f.write(custom_content)
        
        print(f"📝 Created temporary FBA script: {temp_script_path}")
        return temp_script_path
        
    except Exception as e:
        print(f"❌ Error creating FBA script: {e}")
        raise

def execute_fba_script(script_path: str, config_override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the FBA script and collect results
    
    Args:
        script_path (str): Path to the FBA script
        config_override (Dict): Configuration override
        
    Returns:
        Dict containing execution results
    """
    try:
        import subprocess
        import sys
        
        print(f"🚀 Executing FBA script: {script_path}")
        
        # Execute the script
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        if result.returncode == 0:
            print("✅ FBA script executed successfully")
            
            # Collect results from output directory
            output_dir = config_override.get('output_config', {}).get('output_directory', '')
            results = collect_fba_results(output_dir)
            
            return {
                'execution_success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'results': results
            }
        else:
            print(f"❌ FBA script execution failed")
            print(f"Error: {result.stderr}")
            
            return {
                'execution_success': False,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'error': 'Script execution failed'
            }
            
    except subprocess.TimeoutExpired:
        print("⏰ FBA script execution timed out")
        return {
            'execution_success': False,
            'error': 'Script execution timed out'
        }
    except Exception as e:
        print(f"❌ Error executing FBA script: {e}")
        return {
            'execution_success': False,
            'error': str(e)
        }

def collect_fba_results(output_directory: str) -> Dict[str, Any]:
    """
    Collect FBA analysis results from output directory
    
    Args:
        output_directory (str): Output directory path
        
    Returns:
        Dict containing collected results
    """
    results = {
        'files_generated': [],
        'data_files': {},
        'visualization_files': [],
        'analysis_summary': {}
    }
    
    try:
        # Check multiple possible output directories
        possible_dirs = [
            output_directory,
            "/tmp/fba_analysis",
            "/tmp/fba_analysis_e_coli_core"
        ]
        
        actual_output_dir = None
        for dir_path in possible_dirs:
            if os.path.exists(dir_path):
                actual_output_dir = dir_path
                break
        
        if actual_output_dir is None:
            print(f"⚠️ No output directory found. Checked: {possible_dirs}")
            return results
        
        print(f"📁 Found output directory: {actual_output_dir}")
        
        # List all files in output directory
        for file in os.listdir(actual_output_dir):
            file_path = os.path.join(actual_output_dir, file)
            
            if os.path.isfile(file_path):
                results['files_generated'].append(file)
                
                if file.endswith('.csv'):
                    # Data files
                    results['data_files'][file] = {
                        'path': file_path,
                        'size': os.path.getsize(file_path),
                        'type': 'data'
                    }
                    
                elif file.endswith('.json'):
                    # JSON files
                    try:
                        import json
                        with open(file_path, 'r') as f:
                            results['data_files'][file] = json.load(f)
                    except Exception as e:
                        print(f"❌ Error loading JSON file {file}: {e}")
                        results['data_files'][file] = {
                            'path': file_path,
                            'size': os.path.getsize(file_path),
                            'type': 'json',
                            'error': str(e)
                        }
                    
                elif file.endswith('.png') or file.endswith('.jpg') or file.endswith('.pdf'):
                    # Visualization files
                    results['visualization_files'].append({
                        'name': file,
                        'path': file_path,
                        'type': 'visualization',
                        'size': os.path.getsize(file_path)
                    })
        
        # Try to read and parse key data files
        results['analysis_summary'] = parse_fba_data_files(results['data_files'])
        
        print(f"📊 Collected {len(results['files_generated'])} files from FBA analysis")
        print(f"📈 Found {len(results['visualization_files'])} visualization files")
        
    except Exception as e:
        print(f"❌ Error collecting FBA results: {e}")
        import traceback
        traceback.print_exc()
    
    return results

def parse_fba_data_files(data_files: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse FBA data files to extract key information
    
    Args:
        data_files (Dict): Dictionary of data files
        
    Returns:
        Dict containing parsed analysis summary
    """
    summary = {
        'total_reactions': 0,
        'significant_reactions': 0,
        'growth_rate': 0.0,
        'glucose_sensitivity': {},
        'oxygen_sensitivity': {},
        'gene_knockout_results': []
    }
    
    try:
        import pandas as pd
        
        # Parse flux distribution
        if 'flux_distribution.csv' in data_files:
            flux_file = data_files['flux_distribution.csv']['path']
            if os.path.exists(flux_file):
                flux_df = pd.read_csv(flux_file)
                summary['total_reactions'] = len(flux_df)
                summary['significant_reactions'] = len(flux_df[flux_df['Flux_Value'] != 0])
                
                # Find biomass reaction
                biomass_reactions = flux_df[flux_df['Reaction_ID'].str.contains('BIOMASS', na=False)]
                if not biomass_reactions.empty:
                    summary['growth_rate'] = biomass_reactions.iloc[0]['Flux_Value']
        
        # Parse sensitivity analysis
        if 'sensitivity_analysis.csv' in data_files:
            sensitivity_file = data_files['sensitivity_analysis.csv']['path']
            if os.path.exists(sensitivity_file):
                sensitivity_df = pd.read_csv(sensitivity_file)
                summary['glucose_sensitivity'] = {
                    'rates': sensitivity_df['Glucose_Rate'].tolist(),
                    'growth_rates': sensitivity_df['Growth_Rate'].tolist()
                }
        
        # Parse pathway analysis
        if 'pathway_analysis.csv' in data_files:
            pathway_file = data_files['pathway_analysis.csv']['path']
            if os.path.exists(pathway_file):
                pathway_df = pd.read_csv(pathway_file)
                summary['pathway_distribution'] = pathway_df['Category'].value_counts().to_dict()
        
    except Exception as e:
        print(f"❌ Error parsing FBA data files: {e}")
    
    return summary

def collect_fba_visualization_files(output_directory: str) -> List[Dict[str, str]]:
    """
    Collect FBA visualization files
    
    Args:
        output_directory (str): Output directory path
        
    Returns:
        List of visualization file information
    """
    visualizations = []
    
    try:
        if not os.path.exists(output_directory):
            return visualizations
        
        for file in os.listdir(output_directory):
            if file.endswith(('.png', '.jpg', '.pdf')):
                file_path = os.path.join(output_directory, file)
                visualizations.append({
                    'name': file,
                    'path': file_path,
                    'type': 'fba_visualization',
                    'size': os.path.getsize(file_path)
                })
        
        print(f"📊 Collected {len(visualizations)} FBA visualization files")
        
    except Exception as e:
        print(f"❌ Error collecting FBA visualization files: {e}")
    
    return visualizations

def generate_fba_analysis_summary(results: Dict[str, Any], config_override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a comprehensive summary of FBA analysis results
    
    Args:
        results (Dict): Analysis results
        config_override (Dict): Configuration used
        
    Returns:
        Dict containing analysis summary
    """
    try:
        import datetime
        
        model_name = config_override.get('model_config', {}).get('model_name', 'Unknown')
        analysis_summary = results.get('analysis_summary', {})
        
        summary = {
            'model_info': {
                'model_name': model_name,
                'analysis_type': 'Flux Balance Analysis (FBA)',
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            'analysis_scope': {
                'total_reactions': analysis_summary.get('total_reactions', 0),
                'significant_reactions': analysis_summary.get('significant_reactions', 0),
                'glucose_rates_tested': len(config_override.get('analysis_config', {}).get('glucose_uptake_rates', [])),
                'oxygen_rates_tested': len(config_override.get('analysis_config', {}).get('oxygen_availability_rates', [])),
                'genes_tested': len(config_override.get('analysis_config', {}).get('test_genes', []))
            },
            'key_results': {
                'optimal_growth_rate': analysis_summary.get('growth_rate', 0.0),
                'pathway_distribution': analysis_summary.get('pathway_distribution', {}),
                'glucose_sensitivity': analysis_summary.get('glucose_sensitivity', {}),
                'oxygen_sensitivity': analysis_summary.get('oxygen_sensitivity', {})
            },
            'output_files': {
                'total_files': len(results.get('files_generated', [])),
                'data_files': len(results.get('data_files', {})),
                'visualization_files': len(results.get('visualization_files', []))
            },
            'results_available': [
                'flux_distribution',
                'pathway_analysis', 
                'sensitivity_analysis',
                'gene_knockout_analysis',
                'visualizations'
            ]
        }
        
        return summary
        
    except Exception as e:
        print(f"❌ Error generating FBA analysis summary: {e}")
        return {}

def generate_fba_analysis_report(analysis_results: Dict[str, Any], model_name: str) -> str:
    """
    Generate comprehensive FBA analysis report using LLM
    
    Args:
        analysis_results (Dict): Analysis results
        model_name (str): Name of the model
        
    Returns:
        str: Generated report
    """
    try:
        from agent.code_writer import CodeWriterAgent
        
        # Initialize LLM agent
        llm_agent = CodeWriterAgent()
        
        # Prepare analysis data for LLM
        results = analysis_results.get('results', {})
        stdout = results.get('stdout', '')
        collected_results = results.get('results', {})
        data_files = collected_results.get('data_files', {})
        
        # Create prompt for LLM
        prompt = f"""
Please generate a comprehensive experimental report for Flux Balance Analysis (FBA) of the {model_name} metabolic model.

Analysis Output:
{stdout}

Data Files Generated:
{list(data_files.keys()) if data_files else 'No data files generated'}

Visualization Files:
{analysis_results.get('visualizations', [])}

Please create a detailed report following this structure:
1. Executive Summary
2. Model Overview
3. Key Experimental Findings
   - Growth Rate Analysis
   - Flux Distribution Analysis
   - Sensitivity Analysis (Glucose and Oxygen)
   - Gene Knockout Analysis
   - Pathway Analysis
4. Major Conclusions
5. Experimental Significance
6. Limitations and Future Directions
7. Methods Summary

Make the report comprehensive and scientifically accurate.
Include quantitative results, growth rates, flux distributions, and sensitivity data.
Mention the visualization files that were generated.
"""
        
        # Generate report using LLM
        report = llm_agent.chat(prompt)
        
        # Save report to file
        report_file = f"ResultsData/fba_analysis_report_{model_name}.txt"
        os.makedirs("ResultsData", exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📋 Generated comprehensive FBA report: {report_file}")
        return report
        
    except Exception as e:
        print(f"❌ Error generating FBA report: {e}")
        return f"Error generating report: {str(e)}"

def save_fba_analysis_results(analysis_results: Dict[str, Any], model_name: str) -> str:
    """
    Save FBA analysis results to file
    
    Args:
        analysis_results (Dict): Analysis results
        model_name (str): Name of the model
        
    Returns:
        str: Path to the saved results file
    """
    try:
        # Create Temp directory if it doesn't exist
        temp_dir = "Temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Prepare complete results with success status
        complete_results = {
            'success': True,  # Analysis completed successfully
            'model_name': model_name,
            'task_type': 1,  # FBA Analysis
            'analysis_completed': analysis_results.get('analysis_completed', True),
            'summary': analysis_results.get('summary', ''),
            'results': analysis_results.get('results', {}),
            'visualizations': analysis_results.get('visualizations', []),
            'config_used': analysis_results.get('config_used', {}),
            'output_directory': analysis_results.get('output_directory', '')
        }
        
        # Save detailed results
        results_file = os.path.join(temp_dir, f"fba_results_{model_name}.json")
        with open(results_file, 'w') as f:
            json.dump(complete_results, f, indent=2, default=str)
        
        # Save summary
        summary_file = os.path.join(temp_dir, f"fba_summary_{model_name}.json")
        with open(summary_file, 'w') as f:
            json.dump(analysis_results.get('summary', {}), f, indent=2, default=str)
        
        print(f"💾 FBA results saved to: {results_file}")
        print(f"📋 FBA summary saved to: {summary_file}")
        
        return results_file
        
    except Exception as e:
        print(f"❌ Error saving FBA analysis results: {e}")
        raise

def get_fba_analysis_status(model_name: str) -> Optional[Dict[str, Any]]:
    """
    Get status of FBA analysis for a specific model
    
    Args:
        model_name (str): Name of the model
        
    Returns:
        Optional[Dict]: Analysis status information
    """
    try:
        temp_dir = "Temp"
        results_file = os.path.join(temp_dir, f"fba_results_{model_name}.json")
        summary_file = os.path.join(temp_dir, f"fba_summary_{model_name}.json")
        
        if os.path.exists(results_file) and os.path.exists(summary_file):
            with open(results_file, 'r') as f:
                results = json.load(f)
            with open(summary_file, 'r') as f:
                summary = json.load(f)
            
            return {
                'model_name': model_name,
                'analysis_type': 'FBA',
                'status': 'completed',
                'results': results,
                'summary': summary,
                'results_file': results_file,
                'summary_file': summary_file
            }
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error getting FBA analysis status: {e}")
        return None

def list_fba_analyses() -> List[Dict[str, Any]]:
    """
    List all available FBA analyses
    
    Returns:
        List of analysis information
    """
    try:
        temp_dir = "Temp"
        analyses = []
        
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                if file.startswith("fba_results_") and file.endswith(".json"):
                    model_name = file.replace("fba_results_", "").replace(".json", "")
                    analysis_data = get_fba_analysis_status(model_name)
                    if analysis_data:
                        analyses.append(analysis_data)
        
        return analyses
        
    except Exception as e:
        print(f"❌ Error listing FBA analyses: {e}")
        return []


def execute_phenotype_prediction(model_name: str, model_location: str) -> Dict[str, Any]:
    """
    Execute Phenotype Prediction analysis
    
    Args:
        model_name (str): Name of the model
        model_location (str): Location of the model file
        
    Returns:
        Dict containing execution status and results
    """
    try:
        print(f"🔬 EXECUTE_PHENOTYPE_PREDICTION METHOD CALLED for {model_name}")
        print(f"📁 Model location: {model_location}")
        
        # TODO: Implement Phenotype Prediction analysis
        # This method is under development
        
        return {
            'success': False,
            'error': 'Phenotype Prediction method is under development',
            'model_name': model_name,
            'model_location': model_location,
            'analysis_type': 'Phenotype_Prediction',
            'message': 'This analysis method is currently being implemented. Please check back later.',
            'status': 'under_development'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error in Phenotype Prediction execution: {str(e)}',
            'model_name': model_name,
            'model_location': model_location,
            'analysis_type': 'Phenotype_Prediction'
        }


def execute_pathway_analysis(model_name: str, model_location: str) -> Dict[str, Any]:
    """
    Execute Pathway Analysis
    
    Args:
        model_name (str): Name of the model
        model_location (str): Location of the model file
        
    Returns:
        Dict containing execution status and results
    """
    try:
        print(f"🔬 EXECUTE_PATHWAY_ANALYSIS METHOD CALLED for {model_name}")
        print(f"📁 Model location: {model_location}")
        
        # TODO: Implement Pathway Analysis
        # This method is under development
        
        return {
            'success': False,
            'error': 'Pathway Analysis method is under development',
            'model_name': model_name,
            'model_location': model_location,
            'analysis_type': 'Pathway_Analysis',
            'message': 'This analysis method is currently being implemented. Please check back later.',
            'status': 'under_development'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error in Pathway Analysis execution: {str(e)}',
            'model_name': model_name,
            'model_location': model_location,
            'analysis_type': 'Pathway_Analysis'
        }


def execute_evolutionary_analysis(model_name: str, model_location: str) -> Dict[str, Any]:
    """
    Execute Evolutionary Analysis
    
    Args:
        model_name (str): Name of the model
        model_location (str): Location of the model file
        
    Returns:
        Dict containing execution status and results
    """
    try:
        print(f"🔬 EXECUTE_EVOLUTIONARY_ANALYSIS METHOD CALLED for {model_name}")
        print(f"📁 Model location: {model_location}")
        
        # TODO: Implement Evolutionary Analysis
        # This method is under development
        
        return {
            'success': False,
            'error': 'Evolutionary Analysis method is under development',
            'model_name': model_name,
            'model_location': model_location,
            'analysis_type': 'Evolutionary_Analysis',
            'message': 'This analysis method is currently being implemented. Please check back later.',
            'status': 'under_development'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error in Evolutionary Analysis execution: {str(e)}',
            'model_name': model_name,
            'model_location': model_location,
            'analysis_type': 'Evolutionary_Analysis'
        }


def execute_constraint_based_analysis(model_name: str, model_location: str) -> Dict[str, Any]:
    """
    Execute Constraint-Based Analysis using the Constraint-Based Analysis template
    
    Args:
        model_name (str): Name of the model to experiment with
        model_location (str): Location of the model file
        
    Returns:
        Dict containing execution status and results
    """
    try:
        # Add timestamp and clear call indication
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "="*80)
        print(f"🔬 EXECUTE_CONSTRAINT_BASED_ANALYSIS METHOD CALLED")
        print(f"⏰ Timestamp: {timestamp}")
        print(f"🎯 Model: {model_name}")
        print(f"📁 Location: {model_location}")
        print(f"🔄 Status: Starting Constraint-Based Analysis...")
        print("="*80)
        
        print(f"🚀 Starting Constraint-Based Analysis for model: {model_name}")
        print(f"📁 Model location: {model_location}")
        
        # Verify model file exists
        if not os.path.exists(model_location):
            return {
                'success': False,
                'error': f"Model file not found: {model_location}",
                'model_name': model_name,
                'model_location': model_location
            }
        
        # Read bio_task content and create configuration override
        config_override = create_constraint_based_config_from_bio_task(model_name, model_location)
        
        # Execute Constraint-Based Analysis using the template
        analysis_results = execute_constraint_based_analysis_template(config_override)
        
        # Save analysis results
        results_file = save_constraint_based_analysis_results(analysis_results, model_name)
        
        # Generate comprehensive report using LLM
        report = generate_constraint_based_analysis_report(analysis_results, model_name)
        
        # Add completion timestamp
        completion_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"✅ Constraint-Based Analysis completed for {model_name}")
        print(f"📄 Results saved to: {results_file}")
        print(f"📋 Report generated: {len(report)} characters")
        
        print("="*80)
        print(f"🎉 EXECUTE_CONSTRAINT_BASED_ANALYSIS METHOD COMPLETED SUCCESSFULLY")
        print(f"⏰ Completion Time: {completion_timestamp}")
        print(f"📊 Results: Analysis completed and saved")
        print("="*80 + "\n")
        
        # Extract visualization file paths from the collected visualizations
        visualization_paths = []
        if analysis_results.get('visualizations'):
            for viz in analysis_results['visualizations']:
                if isinstance(viz, dict) and 'path' in viz:
                    visualization_paths.append(viz['path'])
                elif isinstance(viz, str):
                    visualization_paths.append(viz)
        
        return {
            'success': True,
            'results': analysis_results,
            'results_file': results_file,
            'report': report,
            'model_name': model_name,
            'model_location': model_location,
            'task_type': 6,  # Constraint-Based Analysis
            'visualizations': visualization_paths,
            'reports': analysis_results.get('reports', [])
        }
        
    except Exception as e:
        # Add error timestamp
        error_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        error_result = {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc(),
            'model_name': model_name,
            'model_location': model_location
        }
        
        print(f"❌ Error in Constraint-Based Analysis: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        
        print("="*80)
        print(f"💥 EXECUTE_CONSTRAINT_BASED_ANALYSIS METHOD FAILED")
        print(f"⏰ Error Time: {error_timestamp}")
        print(f"❌ Error: {str(e)}")
        print("="*80 + "\n")
        
        return error_result

def create_constraint_based_config_from_bio_task(model_name: str, model_location: str) -> Dict[str, Any]:
    """
    Create Constraint-Based Analysis configuration from bio_task information
    
    Args:
        model_name (str): Name of the model
        model_location (str): Location of the model file
        
    Returns:
        Dict containing Constraint-Based Analysis configuration
    """
    try:
        # Get current bio_task
        current_task = get_current_task()
        
        # Determine model format based on file extension
        model_format = "auto"
        if model_location.endswith('.xml') or model_location.endswith('.sbml'):
            model_format = "sbml"
        elif model_location.endswith('.json'):
            model_format = "json"
        elif model_location.endswith('.mat'):
            model_format = "mat"
        
        # Create configuration override for Constraint-Based Analysis
        config_override = {
            'model_name': model_name,
            'model_file_path': model_location,
            'output_directory': f"/tmp/constraint_analysis_{model_name}",
            'model_loading_options': {
                'model_format': model_format,
                'preprocess_model': True,
                'remove_blocked_reactions': False,
                'set_objective': None  # Will use model's default objective
            },
            'analysis_parameters': {
                'essentiality_threshold': 0.01,
                'carbon_sources': ['glucose', 'fructose', 'acetate', 'succinate', 'lactate', 'glycerol', 'pyruvate'],
                'carbon_exchange_mapping': {
                    'glucose': 'EX_glc__D_e',
                    'fructose': 'EX_fru_e',
                    'acetate': 'EX_ac_e',
                    'succinate': 'EX_succ_e',
                    'lactate': 'EX_lac__L_e',
                    'glycerol': 'EX_glyc_e',
                    'pyruvate': 'EX_pyr_e'
                },
                'environmental_conditions': ['pH', 'temperature', 'osmotic'],
                'ph_conditions': {
                    'Acidic (pH 5)': 10.0,
                    'Neutral (pH 7)': 0.0,
                    'Basic (pH 9)': -10.0
                },
                'temperature_conditions': {
                    'Low (20°C)': 5.0,
                    'Optimal (37°C)': 8.39,
                    'High (45°C)': 15.0
                },
                'central_reactions': [
                    'PGI', 'PFK', 'FBA', 'TPI', 'GAPD', 'PGK', 'PGM', 'ENO', 'PYK',
                    'CS', 'ACONT', 'ICDHyr', 'AKGDH', 'SUCOAS', 'SUCDi', 'FUM', 'MDH'
                ],
                'perform_basic_info': True,
                'perform_fba': True,
                'perform_growth_analysis': True,
                'perform_environmental_analysis': True,
                'perform_essentiality_analysis': True,
                'create_visualizations': True
            }
        }
        
        print(f"📋 Created Constraint-Based Analysis configuration for {model_name}")
        print(f"📁 Output directory: {config_override['output_directory']}")
        print(f"🔬 Analysis parameters: {len(config_override['analysis_parameters']['carbon_sources'])} carbon sources, {len(config_override['analysis_parameters']['central_reactions'])} central reactions")
        
        return config_override
        
    except Exception as e:
        print(f"❌ Error creating Constraint-Based Analysis configuration: {e}")
        raise

def execute_constraint_based_analysis_template(config_override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Constraint-Based Analysis using the template
    
    Args:
        config_override (Dict): Configuration override for the analysis
        
    Returns:
        Dict containing analysis results
    """
    try:
        print("📋 Initializing Constraint-Based Analysis Template...")
        
        # Create a temporary script with the configuration
        temp_script = create_constraint_based_script_from_config(config_override)
        
        print("🔬 Running complete Constraint-Based Analysis...")
        
        # Execute the Constraint-Based Analysis
        results = execute_constraint_based_script(temp_script, config_override)
        
        # Collect visualization files
        visualizations = collect_constraint_based_visualization_files(config_override.get('output_directory', ''))
        
        # Generate analysis summary
        summary = generate_constraint_based_analysis_summary(results, config_override)
        
        # Compile comprehensive results
        analysis_results = {
            'analysis_completed': True,
            'summary': summary,
            'results': results,
            'visualizations': visualizations,
            'config_used': config_override,
            'output_directory': config_override.get('output_directory', '')
        }
        
        # Clean up temporary script
        if os.path.exists(temp_script):
            os.remove(temp_script)
        
        print("✅ Constraint-Based Analysis completed successfully")
        
        return analysis_results
        
    except Exception as e:
        print(f"❌ Error executing Constraint-Based Analysis: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise

def create_constraint_based_script_from_config(config_override: Dict[str, Any]) -> str:
    """
    Create a custom Constraint-Based Analysis script from configuration
    
    Args:
        config_override (Dict): Configuration override
        
    Returns:
        str: Path to the temporary script
    """
    try:
        # Read the Constraint-Based Analysis template
        template_path = "CodeTemplate/Constraint-Based Analysis/constraint_based_analysis_template.py"
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Replace slots with actual values
        custom_content = template_content
        
        # Replace model file path
        model_file_path = config_override.get('model_file_path', '')
        custom_content = custom_content.replace('"{{model_file_path}}"', f'"{model_file_path}"')
        
        # Replace output directory
        output_directory = config_override.get('output_directory', '')
        custom_content = custom_content.replace('"{{output_directory}}"', f'"{output_directory}"')
        
        # Replace analysis parameters
        analysis_params = config_override.get('analysis_parameters', {})
        
        # Essentiality threshold
        threshold = analysis_params.get('essentiality_threshold', 0.01)
        custom_content = custom_content.replace('{{essentiality_threshold}}', str(threshold))
        
        # Carbon sources
        carbon_sources = analysis_params.get('carbon_sources', ['glucose'])
        custom_content = custom_content.replace('{{carbon_sources}}', str(carbon_sources))
        
        # Carbon exchange mapping
        carbon_mapping = analysis_params.get('carbon_exchange_mapping', {'glucose': 'EX_glc__D_e'})
        custom_content = custom_content.replace('{{carbon_exchange_mapping}}', str(carbon_mapping))
        
        # Environmental conditions
        env_conditions = analysis_params.get('environmental_conditions', ['pH', 'temperature'])
        custom_content = custom_content.replace('{{environmental_conditions}}', str(env_conditions))
        
        # pH conditions
        ph_conditions = analysis_params.get('ph_conditions', {'Neutral': 0.0})
        custom_content = custom_content.replace('{{ph_conditions}}', str(ph_conditions))
        
        # Temperature conditions
        temp_conditions = analysis_params.get('temperature_conditions', {'Optimal': 8.39})
        custom_content = custom_content.replace('{{temperature_conditions}}', str(temp_conditions))
        
        # Central reactions
        central_reactions = analysis_params.get('central_reactions', ['PGI', 'PFK', 'FBA'])
        custom_content = custom_content.replace('{{central_reactions}}', str(central_reactions))
        
        # Analysis options
        for option in ['perform_basic_info', 'perform_fba', 'perform_growth_analysis', 
                       'perform_environmental_analysis', 'perform_essentiality_analysis', 'create_visualizations']:
            value = analysis_params.get(option, True)
            custom_content = custom_content.replace(f'{{{{{option}}}}}', str(value))
        
        # Replace model loading options
        model_options = config_override.get('model_loading_options', {})
        
        model_format = model_options.get('model_format', 'auto')
        custom_content = custom_content.replace('{{model_format}}', f'"{model_format}"')
        
        preprocess = model_options.get('preprocess_model', False)
        custom_content = custom_content.replace('{{preprocess_model}}', str(preprocess))
        
        remove_blocked = model_options.get('remove_blocked_reactions', False)
        custom_content = custom_content.replace('{{remove_blocked_reactions}}', str(remove_blocked))
        
        objective = model_options.get('set_objective', None)
        if objective:
            custom_content = custom_content.replace('{{set_objective}}', f'"{objective}"')
        else:
            custom_content = custom_content.replace('{{set_objective}}', 'None')
        
        # Write the custom script
        model_name = config_override.get('model_name', 'analysis')
        if not model_name:
            # Extract model name from file path if not provided
            model_file_path = config_override.get('model_file_path', '')
            if model_file_path:
                model_name = os.path.splitext(os.path.basename(model_file_path))[0]
            else:
                model_name = 'analysis'
        
        temp_script_path = f"Temp/temp_constraint_based_{model_name}.py"
        os.makedirs(os.path.dirname(temp_script_path), exist_ok=True)
        
        with open(temp_script_path, 'w') as f:
            f.write(custom_content)
        
        print(f"📝 Created temporary Constraint-Based Analysis script: {temp_script_path}")
        return temp_script_path
        
    except Exception as e:
        print(f"❌ Error creating Constraint-Based Analysis script: {e}")
        raise

def execute_constraint_based_script(script_path: str, config_override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute the Constraint-Based Analysis script and collect results
    
    Args:
        script_path (str): Path to the Constraint-Based Analysis script
        config_override (Dict): Configuration override
        
    Returns:
        Dict containing execution results
    """
    try:
        import subprocess
        import sys
        
        print(f"🚀 Executing Constraint-Based Analysis script: {script_path}")
        
        # Execute the script
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, timeout=900)  # 15 minute timeout
        
        if result.returncode == 0:
            print("✅ Constraint-Based Analysis script executed successfully")
            
            # Collect results from output directory
            output_dir = config_override.get('output_directory', '')
            results = collect_constraint_based_results(output_dir)
            
            return {
                'execution_success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'results': results
            }
        else:
            print(f"❌ Constraint-Based Analysis script execution failed")
            print(f"Error: {result.stderr}")
            
            return {
                'execution_success': False,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'error': 'Script execution failed'
            }
            
    except subprocess.TimeoutExpired:
        print("⏰ Constraint-Based Analysis script execution timed out")
        return {
            'execution_success': False,
            'error': 'Script execution timed out'
        }
    except Exception as e:
        print(f"❌ Error executing Constraint-Based Analysis script: {e}")
        return {
            'execution_success': False,
            'error': str(e)
        }

def collect_constraint_based_results(output_directory: str) -> Dict[str, Any]:
    """
    Collect Constraint-Based Analysis results from output directory
    
    Args:
        output_directory (str): Output directory path
        
    Returns:
        Dict containing collected results
    """
    results = {
        'files_generated': [],
        'data_files': {},
        'visualization_files': [],
        'analysis_summary': {}
    }
    
    try:
        if not os.path.exists(output_directory):
            print(f"⚠️ Output directory not found: {output_directory}")
            return results
        
        # List all files in output directory
        for file in os.listdir(output_directory):
            file_path = os.path.join(output_directory, file)
            
            if os.path.isfile(file_path):
                results['files_generated'].append(file)
                
                # Categorize files
                if file.endswith('.json'):
                    # Load JSON data
                    try:
                        with open(file_path, 'r') as f:
                            results['data_files'][file] = json.load(f)
                    except:
                        results['data_files'][file] = "Error loading JSON"
                elif file.endswith('.txt'):
                    # Load text data
                    try:
                        with open(file_path, 'r') as f:
                            results['data_files'][file] = f.read()
                    except:
                        results['data_files'][file] = "Error loading text"
                elif file.endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                    results['visualization_files'].append(file)
        
        print(f"📊 Collected {len(results['files_generated'])} files from output directory")
        print(f"📈 Found {len(results['visualization_files'])} visualization files")
        
        return results
        
    except Exception as e:
        print(f"❌ Error collecting Constraint-Based Analysis results: {e}")
        return results

def collect_constraint_based_visualization_files(output_directory: str) -> List[str]:
    """
    Collect visualization files from Constraint-Based Analysis output directory
    
    Args:
        output_directory (str): Output directory path
        
    Returns:
        List of visualization file paths
    """
    visualizations = []
    
    try:
        if not os.path.exists(output_directory):
            return visualizations
        
        for file in os.listdir(output_directory):
            if file.endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                visualizations.append(os.path.join(output_directory, file))
        
        print(f"📊 Found {len(visualizations)} visualization files")
        return visualizations
        
    except Exception as e:
        print(f"❌ Error collecting visualization files: {e}")
        return visualizations

def generate_constraint_based_analysis_summary(results: Dict[str, Any], config_override: Dict[str, Any]) -> str:
    """
    Generate a summary of Constraint-Based Analysis results
    
    Args:
        results (Dict): Analysis results
        config_override (Dict): Configuration used
        
    Returns:
        str: Analysis summary
    """
    try:
        summary = f"Constraint-Based Analysis Summary\n"
        summary += f"Model: {config_override.get('model_file_path', 'Unknown')}\n"
        summary += f"Output Directory: {config_override.get('output_directory', 'Unknown')}\n"
        summary += f"Files Generated: {len(results.get('files_generated', []))}\n"
        summary += f"Visualizations: {len(results.get('visualization_files', []))}\n"
        
        # Add key results if available
        if 'data_files' in results:
            for file_name, data in results['data_files'].items():
                if isinstance(data, dict):
                    summary += f"\n{file_name}:\n"
                    for key, value in data.items():
                        if isinstance(value, (int, float, str)):
                            summary += f"  {key}: {value}\n"
        
        return summary
        
    except Exception as e:
        print(f"❌ Error generating analysis summary: {e}")
        return "Error generating summary"

def save_constraint_based_analysis_results(analysis_results: Dict[str, Any], model_name: str) -> str:
    """
    Save Constraint-Based Analysis results to file
    
    Args:
        analysis_results (Dict): Analysis results
        model_name (str): Name of the model
        
    Returns:
        str: Path to saved results file
    """
    try:
        # Create results directory
        results_dir = "ResultsData"
        os.makedirs(results_dir, exist_ok=True)
        
        # Prepare complete results with success status
        complete_results = {
            'success': True,  # Analysis completed successfully
            'model_name': model_name,
            'task_type': 6,  # Constraint-Based Analysis
            'analysis_completed': analysis_results.get('analysis_completed', True),
            'summary': analysis_results.get('summary', ''),
            'results': analysis_results.get('results', {}),
            'visualizations': analysis_results.get('visualizations', []),
            'config_used': analysis_results.get('config_used', {}),
            'output_directory': analysis_results.get('output_directory', '')
        }
        
        # Save results to JSON file
        results_file = os.path.join(results_dir, f"constraint_based_analysis_{model_name}.json")
        
        with open(results_file, 'w') as f:
            json.dump(complete_results, f, indent=2, default=str)
        
        print(f"💾 Saved Constraint-Based Analysis results to: {results_file}")
        return results_file
        
    except Exception as e:
        print(f"❌ Error saving Constraint-Based Analysis results: {e}")
        return ""

def generate_constraint_based_analysis_report(analysis_results: Dict[str, Any], model_name: str) -> str:
    """
    Generate comprehensive Constraint-Based Analysis report using LLM
    
    Args:
        analysis_results (Dict): Analysis results
        model_name (str): Name of the model
        
    Returns:
        str: Generated report
    """
    try:
        from agent.code_writer import CodeWriterAgent
        
        # Initialize LLM agent
        llm_agent = CodeWriterAgent()
        
        # Prepare analysis data for LLM
        analysis_data = analysis_results.get('results', {}).get('results', {})
        data_files = analysis_data.get('data_files', {})
        
        # Extract key information
        model_info = data_files.get('analysis_results.json', {})
        summary_data = data_files.get('analysis_summary.txt', '')
        
        # Create prompt for LLM
        prompt = f"""
Please generate a comprehensive experimental report for Constraint-Based Analysis of the {model_name} metabolic model.

Analysis Results:
{json.dumps(model_info, indent=2) if isinstance(model_info, dict) else str(model_info)}

Summary Data:
{summary_data}

Visualization Files Generated:
{analysis_results.get('visualizations', [])}

Please create a detailed report following this structure:
1. Executive Summary
2. Model Overview
3. Key Experimental Findings
   - Basic Metabolic Capabilities
   - Carbon Source Utilization
   - Oxygen Dependency
   - Environmental Stress Responses
   - Metabolic Network Robustness
4. Major Conclusions
5. Experimental Significance
6. Limitations and Future Directions
7. Methods Summary

Reference the example format from ResultExample/ConstraintBased.txt for style and structure.
Include quantitative results, growth rates, essential reactions, and environmental responses.
Mention the visualization files that were generated.
Make the report comprehensive and scientifically accurate.
"""
        
        # Generate report using LLM
        report = llm_agent.chat(prompt)
        
        # Save report to file
        report_file = f"ResultsData/constraint_based_analysis_report_{model_name}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📋 Generated comprehensive report: {report_file}")
        return report
        
    except Exception as e:
        print(f"❌ Error generating Constraint-Based Analysis report: {e}")
        return f"Error generating report: {str(e)}"

# Global function for easy access
def execute_gene_deletion_global(model_name: str, model_location: str) -> Dict[str, Any]:
    """
    Global function to execute gene deletion analysis
    
    Args:
        model_name (str): Name of the model
        model_location (str): Location of the model file
        
    Returns:
        Dict containing execution results
    """
    return execute_gene_deletion(model_name, model_location)

# Global function for easy access
def execute_fba_global(model_name: str, model_location: str) -> Dict[str, Any]:
    """
    Global function to execute FBA analysis
    
    Args:
        model_name (str): Name of the model
        model_location (str): Location of the model file
        
    Returns:
        Dict containing execution results
    """
    return execute_fba(model_name, model_location)


