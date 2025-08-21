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
        
        return {
            'success': True,
            'results': analysis_results,
            'results_file': results_file,
            'model_name': model_name,
            'model_location': model_location,
            'visualizations': analysis_results.get('visualizations', []),
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


