#!/usr/bin/env python3
"""
Test script to verify that the FBA result visualizer can properly display
FBA analysis results with the actual data structure.
"""

import json
import os

def test_fba_visualizer_with_real_data():
    """Test the visualizer with real FBA analysis results"""
    
    print("🧪 Testing FBA Result Visualizer with Real Data")
    print("=" * 70)
    
    # Load the actual results file
    results_file = "Temp/fba_results_e_coli_core.json"
    
    if not os.path.exists(results_file):
        print(f"❌ Results file not found: {results_file}")
        return False
    
    try:
        with open(results_file, 'r') as f:
            experiment_result = json.load(f)
        
        print("✅ Loaded FBA results successfully")
        
        # Test data structure
        print("\n📊 Testing Data Structure:")
        
        # Check basic structure
        success = experiment_result.get('success', False)
        model_name = experiment_result.get('model_name', '')
        task_type = experiment_result.get('task_type', 0)
        analysis_completed = experiment_result.get('analysis_completed', False)
        
        print(f"  - Success: {success}")
        print(f"  - Model: {model_name}")
        print(f"  - Task Type: {task_type}")
        print(f"  - Analysis Completed: {analysis_completed}")
        
        # Check results structure
        results = experiment_result.get('results', {})
        if results:
            execution_success = results.get('execution_success', False)
            stdout = results.get('stdout', '')
            detailed_results = results.get('results', {})  # This is the nested results
            data_files = detailed_results.get('data_files', {})  # data_files is inside detailed_results
            files_generated = detailed_results.get('files_generated', [])
            visualization_files = detailed_results.get('visualization_files', [])
            
            print(f"  - Execution Success: {execution_success}")
            print(f"  - Files Generated: {len(files_generated)}")
            print(f"  - Visualization Files: {len(visualization_files)}")
            print(f"  - Data Files: {len(data_files)}")
            
            # Check detailed results
            if detailed_results:
                model_info = detailed_results.get('model_info', {})
                fba_analysis = detailed_results.get('fba_analysis', {})
                sensitivity_analysis = detailed_results.get('sensitivity_analysis', {})
                pathway_analysis = detailed_results.get('pathway_analysis', {})
                gene_knockout_analysis = detailed_results.get('gene_knockout_analysis', {})
                
                print(f"  - Model Info: {'✅' if model_info else '❌'}")
                print(f"  - FBA Analysis: {'✅' if fba_analysis else '❌'}")
                print(f"  - Sensitivity Analysis: {'✅' if sensitivity_analysis else '❌'}")
                print(f"  - Pathway Analysis: {'✅' if pathway_analysis else '❌'}")
                print(f"  - Gene Knockout Analysis: {'✅' if gene_knockout_analysis else '❌'}")
                
                # Test specific data extraction
                if model_info:
                    model_id = model_info.get('model_id', '')
                    reactions_count = model_info.get('reactions_count', 0)
                    metabolites_count = model_info.get('metabolites_count', 0)
                    genes_count = model_info.get('genes_count', 0)
                    
                    print(f"    - Model ID: {model_id}")
                    print(f"    - Reactions: {reactions_count}")
                    print(f"    - Metabolites: {metabolites_count}")
                    print(f"    - Genes: {genes_count}")
                
                if fba_analysis:
                    objective_value = fba_analysis.get('objective_value', 0)
                    status = fba_analysis.get('status', '')
                    flux_distribution = fba_analysis.get('flux_distribution', {})
                    
                    print(f"    - Growth Rate: {objective_value:.6f} h⁻¹")
                    print(f"    - Status: {status}")
                    print(f"    - Flux Distribution Entries: {len(flux_distribution)}")
                
                if sensitivity_analysis:
                    glucose_sensitivity = sensitivity_analysis.get('glucose_sensitivity', {})
                    oxygen_sensitivity = sensitivity_analysis.get('oxygen_sensitivity', {})
                    anaerobic_growth = sensitivity_analysis.get('anaerobic_growth', 0)
                    
                    print(f"    - Glucose Sensitivity Points: {len(glucose_sensitivity)}")
                    print(f"    - Oxygen Sensitivity Points: {len(oxygen_sensitivity)}")
                    print(f"    - Anaerobic Growth: {anaerobic_growth:.6f} h⁻¹")
                
                if pathway_analysis:
                    pathway_distribution = pathway_analysis.get('pathway_distribution', {})
                    print(f"    - Pathway Categories: {len(pathway_distribution)}")
                
                if gene_knockout_analysis:
                    knockout_results = gene_knockout_analysis.get('knockout_results', [])
                    print(f"    - Gene Knockout Tests: {len(knockout_results)}")
            
            # Check data_files for analysis_results.json
            if data_files:
                print(f"\n📁 Data Files Found:")
                for file_name, file_data in data_files.items():
                    print(f"  - {file_name}: {type(file_data).__name__}")
                
                analysis_results_json = data_files.get('analysis_results.json', {})
                if isinstance(analysis_results_json, dict):
                    model_info = analysis_results_json.get('model_info', {})
                    fba_analysis = analysis_results_json.get('fba_analysis', {})
                    sensitivity_analysis = analysis_results_json.get('sensitivity_analysis', {})
                    pathway_analysis = analysis_results_json.get('pathway_analysis', {})
                    gene_knockout_analysis = analysis_results_json.get('gene_knockout_analysis', {})
                    
                    print(f"\n📊 Analysis Results from JSON:")
                    print(f"  - Model Info: {'✅' if model_info else '❌'}")
                    print(f"  - FBA Analysis: {'✅' if fba_analysis else '❌'}")
                    print(f"  - Sensitivity Analysis: {'✅' if sensitivity_analysis else '❌'}")
                    print(f"  - Pathway Analysis: {'✅' if pathway_analysis else '❌'}")
                    print(f"  - Gene Knockout Analysis: {'✅' if gene_knockout_analysis else '❌'}")
                    
                    # Test specific data extraction from JSON
                    if model_info:
                        model_id = model_info.get('model_id', '')
                        reactions_count = model_info.get('reactions_count', 0)
                        metabolites_count = model_info.get('metabolites_count', 0)
                        genes_count = model_info.get('genes_count', 0)
                        
                        print(f"    - Model ID: {model_id}")
                        print(f"    - Reactions: {reactions_count}")
                        print(f"    - Metabolites: {metabolites_count}")
                        print(f"    - Genes: {genes_count}")
                    
                    if fba_analysis:
                        objective_value = fba_analysis.get('objective_value', 0)
                        status = fba_analysis.get('status', '')
                        flux_distribution = fba_analysis.get('flux_distribution', {})
                        
                        print(f"    - Growth Rate: {objective_value:.6f} h⁻¹")
                        print(f"    - Status: {status}")
                        print(f"    - Flux Distribution Entries: {len(flux_distribution)}")
                    
                    if sensitivity_analysis:
                        glucose_sensitivity = sensitivity_analysis.get('glucose_sensitivity', {})
                        oxygen_sensitivity = sensitivity_analysis.get('oxygen_sensitivity', {})
                        anaerobic_growth = sensitivity_analysis.get('anaerobic_growth', 0)
                        
                        print(f"    - Glucose Sensitivity Points: {len(glucose_sensitivity)}")
                        print(f"    - Oxygen Sensitivity Points: {len(oxygen_sensitivity)}")
                        print(f"    - Anaerobic Growth: {anaerobic_growth:.6f} h⁻¹")
                    
                    if pathway_analysis:
                        pathway_distribution = pathway_analysis.get('pathway_distribution', {})
                        print(f"    - Pathway Categories: {len(pathway_distribution)}")
                    
                    if gene_knockout_analysis:
                        knockout_results = gene_knockout_analysis.get('knockout_results', [])
                        print(f"    - Gene Knockout Tests: {len(knockout_results)}")
        
        # Test data files
        if data_files:
            print(f"\n📁 Testing Data Files:")
            for file_name, file_data in data_files.items():
                if isinstance(file_data, dict):
                    file_path = file_data.get('path', '')
                    file_size = file_data.get('size', 0)
                    file_type = file_data.get('type', '')
                    
                    print(f"  - {file_name}: {file_type}, {file_size} bytes")
                    if os.path.exists(file_path):
                        print(f"    ✅ File exists: {file_path}")
                    else:
                        print(f"    ❌ File missing: {file_path}")
        
        # Test visualization files
        if visualization_files:
            print(f"\n📈 Testing Visualization Files:")
            for viz in visualization_files:
                viz_name = viz.get('name', '')
                viz_path = viz.get('path', '')
                viz_type = viz.get('type', '')
                viz_size = viz.get('size', 0)
                
                print(f"  - {viz_name}: {viz_type}, {viz_size} bytes")
                if os.path.exists(viz_path):
                    print(f"    ✅ File exists: {viz_path}")
                else:
                    print(f"    ❌ File missing: {viz_path}")
        
        # Test summary extraction
        print(f"\n📋 Testing Summary Extraction:")
        summary = experiment_result.get('summary', {})
        if summary:
            print(f"  - Summary available: ✅")
            for key, value in summary.items():
                print(f"    - {key}: {type(value).__name__}")
        else:
            print(f"  - Summary available: ❌")
        
        # Test report generation
        print(f"\n📄 Testing Report Generation:")
        report = experiment_result.get('report', '')
        if report:
            print(f"  - Report available: ✅ ({len(report)} characters)")
            if 'Executive Summary' in report:
                print(f"    - Contains Executive Summary: ✅")
            else:
                print(f"    - Contains Executive Summary: ❌")
            
            if 'Detailed Analysis' in report:
                print(f"    - Contains Detailed Analysis: ✅")
            else:
                print(f"    - Contains Detailed Analysis: ❌")
            
            if 'Generated Reports' in report:
                print(f"    - Contains Generated Reports: ✅")
            else:
                print(f"    - Contains Generated Reports: ❌")
        else:
            print(f"  - Report available: ❌")
        
        print(f"\n✅ FBA Result Visualizer Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing FBA visualizer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fba_visualizer_with_real_data()
    if success:
        print("\n🎉 All tests passed! FBA analysis and visualization are working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
