#!/usr/bin/env python3
"""
Debug script to check FBA and Constraint-Based Analysis execution
"""

import os
import sys
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def debug_bio_task():
    """Debug bio_task content"""
    print("🔍 Debugging bio_task...")
    
    try:
        from bio_task import get_current_task
        current_task = get_current_task()
        print(f"Model name: '{current_task.model_name}'")
        print(f"Model local: '{current_task.model_local}'")
        print(f"Task type: {current_task.task_type}")
        
        if not current_task.model_name or not current_task.model_name.strip():
            print("❌ Model name is empty!")
            return False
        
        if not current_task.model_local or not current_task.model_local.strip():
            print("❌ Model local path is empty!")
            return False
        
        print("✅ bio_task looks good")
        return True
        
    except Exception as e:
        print(f"❌ Error reading bio_task: {e}")
        return False

def debug_experiment_execution(task_type):
    """Debug experiment execution"""
    print(f"\n🔬 Debugging experiment execution for task type {task_type}...")
    
    try:
        from experiment_executor import execute_experiment
        
        # Execute experiment
        result = execute_experiment("e_coli_core", task_type)
        
        print(f"Execution success: {result.get('success', False)}")
        
        if result.get('success', False):
            print("✅ Experiment executed successfully")
            
            # Check results structure
            results = result.get('results', {})
            print(f"Results keys: {list(results.keys())}")
            
            # Check analysis_results
            analysis_results = results.get('results', {})
            print(f"Analysis results keys: {list(analysis_results.keys())}")
            
            # Check data_files
            data_files = analysis_results.get('data_files', {})
            print(f"Data files: {list(data_files.keys())}")
            
            # Check visualizations
            visualizations = result.get('visualizations', [])
            print(f"Visualizations count: {len(visualizations)}")
            for i, viz in enumerate(visualizations):
                print(f"  {i+1}. {viz}")
                if os.path.exists(viz):
                    print(f"     ✅ File exists")
                else:
                    print(f"     ❌ File not found")
            
            # Check if analysis_results.json exists and is loaded
            if 'analysis_results.json' in data_files:
                model_info = data_files['analysis_results.json']
                if isinstance(model_info, dict):
                    print("✅ analysis_results.json is properly loaded")
                    print(f"   Keys: {list(model_info.keys())}")
                    
                    # Check specific sections
                    if 'fba_analysis' in model_info:
                        fba = model_info['fba_analysis']
                        print(f"   FBA analysis keys: {list(fba.keys())}")
                        print(f"   Objective value: {fba.get('objective_value', 'N/A')}")
                        print(f"   Flux distribution count: {len(fba.get('flux_distribution', {}))}")
                    
                    if 'sensitivity_analysis' in model_info:
                        sensitivity = model_info['sensitivity_analysis']
                        print(f"   Sensitivity analysis keys: {list(sensitivity.keys())}")
                        print(f"   Glucose sensitivity count: {len(sensitivity.get('glucose_sensitivity', {}))}")
                        print(f"   Oxygen sensitivity count: {len(sensitivity.get('oxygen_sensitivity', {}))}")
                    
                    if 'pathway_analysis' in model_info:
                        pathway = model_info['pathway_analysis']
                        print(f"   Pathway analysis keys: {list(pathway.keys())}")
                        print(f"   Pathway distribution count: {len(pathway.get('pathway_distribution', {}))}")
                else:
                    print(f"❌ analysis_results.json is not a dict: {type(model_info)}")
            else:
                print("❌ analysis_results.json not found in data_files")
            
        else:
            print(f"❌ Experiment execution failed: {result.get('error', 'Unknown error')}")
            if 'traceback' in result:
                print(f"Traceback: {result['traceback']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during experiment execution: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_result_visualizer(experiment_result, task_type):
    """Debug result visualizer"""
    print(f"\n🎨 Debugging result visualizer for task type {task_type}...")
    
    try:
        from result_visualizer import EnhancedResultVisualizer
        
        visualizer = EnhancedResultVisualizer()
        
        # Test the specific visualization methods
        if task_type == 1:
            print("Testing FBA visualization...")
            # We'll just check the data structure that would be passed to the visualizer
            results = experiment_result.get('results', {})
            analysis_results = results.get('results', {})
            data_files = analysis_results.get('data_files', {})
            
            print(f"Results structure: {bool(results)}")
            print(f"Analysis results structure: {bool(analysis_results)}")
            print(f"Data files structure: {bool(data_files)}")
            print(f"analysis_results.json in data_files: {'analysis_results.json' in data_files}")
            
            if 'analysis_results.json' in data_files:
                model_info = data_files['analysis_results.json']
                print(f"model_info type: {type(model_info)}")
                if isinstance(model_info, dict):
                    print(f"model_info keys: {list(model_info.keys())}")
                else:
                    print(f"model_info content: {model_info}")
            
        elif task_type == 6:
            print("Testing Constraint-Based Analysis visualization...")
            # Similar checks for constraint-based analysis
            results = experiment_result.get('results', {})
            analysis_results = results.get('results', {})
            data_files = analysis_results.get('data_files', {})
            
            print(f"Results structure: {bool(results)}")
            print(f"Analysis results structure: {bool(analysis_results)}")
            print(f"Data files structure: {bool(data_files)}")
            print(f"analysis_results.json in data_files: {'analysis_results.json' in data_files}")
            
            if 'analysis_results.json' in data_files:
                model_info = data_files['analysis_results.json']
                print(f"model_info type: {type(model_info)}")
                if isinstance(model_info, dict):
                    print(f"model_info keys: {list(model_info.keys())}")
                else:
                    print(f"model_info content: {model_info}")
        
    except Exception as e:
        print(f"❌ Error during result visualizer debug: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main debug function"""
    print("🐛 Debugging FBA and Constraint-Based Analysis Issues")
    print("=" * 60)
    
    # Debug bio_task
    if not debug_bio_task():
        print("\n❌ bio_task has issues. Please set up a valid model and task type.")
        return
    
    # Test both task types
    for task_type in [1, 6]:
        print(f"\n{'='*20} Testing Task Type {task_type} {'='*20}")
        
        # Debug experiment execution
        result = debug_experiment_execution(task_type)
        
        if result and result.get('success', False):
            # Debug result visualizer
            debug_result_visualizer(result, task_type)
        else:
            print(f"❌ Cannot debug visualizer for task type {task_type} - execution failed")
    
    print("\n" + "=" * 60)
    print("🔍 Debug completed. Check the output above for issues.")

if __name__ == "__main__":
    main()
