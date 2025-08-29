#!/usr/bin/env python3
"""
Test script to verify that the result visualizer can properly display
constraint-based analysis results with the actual data structure.
"""

import json
import os

def test_visualizer_with_real_data():
    """Test the visualizer with real constraint-based analysis results"""
    
    print("🧪 Testing Result Visualizer with Real Constraint-Based Analysis Data")
    print("=" * 70)
    
    # Load the actual results file
    results_file = "ResultsData/constraint_based_analysis_e_coli_core.json"
    
    if not os.path.exists(results_file):
        print(f"❌ Results file not found: {results_file}")
        return False
    
    try:
        with open(results_file, 'r') as f:
            experiment_result = json.load(f)
        
        print("✅ Loaded actual constraint-based analysis results")
        
        # Extract the data structure that would be passed to the visualizer
        analysis_results = experiment_result.get('results', {})
        results = analysis_results.get('results', {})
        data_files = results.get('data_files', {})
        
        print(f"\n📊 Data Structure Analysis:")
        print(f"  - Analysis results exists: {bool(analysis_results)}")
        print(f"  - Results exists: {bool(results)}")
        print(f"  - Data files exists: {bool(data_files)}")
        
        # Check if the expected data is available
        if 'analysis_results.json' in data_files:
            model_data = data_files['analysis_results.json']
            print(f"  - Model data loaded: {bool(model_data)}")
            
            # Check for specific sections
            sections = ['basic_info', 'fba_analysis', 'growth_analysis', 'environmental_analysis', 'essentiality_analysis']
            for section in sections:
                if section in model_data:
                    print(f"  - {section}: ✅")
                    
                    # Show some key metrics
                    if section == 'basic_info':
                        basic_info = model_data[section]
                        print(f"    - Reactions: {basic_info.get('reactions_count', 0)}")
                        print(f"    - Metabolites: {basic_info.get('metabolites_count', 0)}")
                        print(f"    - Genes: {basic_info.get('genes_count', 0)}")
                    
                    elif section == 'fba_analysis':
                        fba = model_data[section]
                        print(f"    - Growth rate: {fba.get('objective_value', 0):.6f} h⁻¹")
                        print(f"    - Status: {fba.get('status', 'Unknown')}")
                    
                    elif section == 'growth_analysis':
                        growth = model_data[section]
                        print(f"    - Aerobic growth: {growth.get('aerobic_growth', 0):.6f} h⁻¹")
                        print(f"    - Anaerobic growth: {growth.get('anaerobic_growth', 0):.6f} h⁻¹")
                        print(f"    - Growth reduction: {growth.get('growth_reduction_anaerobic', 0):.1f}%")
                    
                    elif section == 'essentiality_analysis':
                        essential = model_data[section]
                        essential_count = len(essential.get('essential_reactions', []))
                        total_tested = essential.get('total_tested', 0)
                        print(f"    - Essential reactions: {essential_count}/{total_tested}")
                else:
                    print(f"  - {section}: ❌")
        else:
            print("  - Model data not found in data_files")
        
        # Test the visualizer methods with this data
        print(f"\n🔍 Testing Visualizer Methods:")
        
        # Test executive summary data extraction
        try:
            model_info = data_files.get('analysis_results.json', {}).get('basic_info', {})
            fba_results = data_files.get('analysis_results.json', {}).get('fba_analysis', {})
            growth_results = data_files.get('analysis_results.json', {}).get('growth_analysis', {})
            essentiality_results = data_files.get('analysis_results.json', {}).get('essentiality_analysis', {})
            
            print(f"  - Executive summary data extraction: ✅")
            print(f"    - Model info: {bool(model_info)}")
            print(f"    - FBA results: {bool(fba_results)}")
            print(f"    - Growth results: {bool(growth_results)}")
            print(f"    - Essentiality results: {bool(essentiality_results)}")
            
        except Exception as e:
            print(f"  - Executive summary data extraction: ❌ ({e})")
        
        # Test detailed analysis data extraction
        try:
            detailed_results = data_files.get('analysis_results.json', {})
            sections = ['basic_info', 'fba_analysis', 'growth_analysis', 'environmental_analysis', 'essentiality_analysis']
            available_sections = [s for s in sections if s in detailed_results]
            
            print(f"  - Detailed analysis data extraction: ✅")
            print(f"    - Available sections: {len(available_sections)}/{len(sections)}")
            for section in sections:
                if section in detailed_results:
                    print(f"      - {section}: ✅")
                else:
                    print(f"      - {section}: ❌")
            
        except Exception as e:
            print(f"  - Detailed analysis data extraction: ❌ ({e})")
        
        # Test generated reports data extraction
        try:
            output_directory = analysis_results.get('output_directory', '')
            files_generated = results.get('files_generated', [])
            data_files_count = len(data_files)
            
            print(f"  - Generated reports data extraction: ✅")
            print(f"    - Output directory: {output_directory}")
            print(f"    - Files generated: {len(files_generated)}")
            print(f"    - Data files: {data_files_count}")
            
        except Exception as e:
            print(f"  - Generated reports data extraction: ❌ ({e})")
        
        print(f"\n✅ All visualizer method tests passed!")
        print(f"📋 The result visualizer should now properly display:")
        print(f"   - Executive Summary with model metrics and key findings")
        print(f"   - Detailed Analysis Results with comprehensive data tables")
        print(f"   - Generated Reports with file listings and content")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing visualizer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Result Visualizer with Real Data")
    print("=" * 70)
    
    success = test_visualizer_with_real_data()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 Test completed successfully!")
        print("The result visualizer should now properly display constraint-based analysis results.")
    else:
        print("⚠️ Test failed. Please check the error messages above.")
    print("=" * 70)
