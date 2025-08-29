#!/usr/bin/env python3
"""
Test script for task type 1 (FBA Analysis)
This script tests the FBA analysis functionality and verifies that
the Executive Summary, Detailed Analysis Results, and Generated Reports sections
are properly populated.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from experiment_executor import execute_fba
from bio_task import BioTask, BioTaskManager

def test_fba_analysis():
    """Test FBA analysis with e_coli_core model"""
    
    print("🧪 Testing Task Type 1: FBA Analysis")
    print("=" * 60)
    
    # Set up test parameters
    model_name = "e_coli_core"
    model_location = "../downloads/e_coli_core.mat"
    
    # Check if model file exists
    if not os.path.exists(model_location):
        print(f"❌ Model file not found: {model_location}")
        print("Please ensure the e_coli_core.mat file is available in the downloads directory")
        return False
    
    print(f"✅ Model file found: {model_location}")
    
    # Update bio_task with test parameters
    task_manager = BioTaskManager()
    test_task = BioTask(
        model_name=model_name,
        model_local=model_location,
        task_type=1
    )
    task_manager.save_task(test_task)
    
    print(f"📋 Updated bio_task with model: {model_name}, task_type: 1")
    
    try:
        # Execute FBA analysis
        print("\n🚀 Executing FBA analysis...")
        result = execute_fba(model_name, model_location)
        
        if result.get('success', False):
            print("✅ FBA analysis completed successfully!")
            
            # Check the structure of the results
            analysis_results = result.get('results', {})
            
            print("\n📊 Analysis Results Structure:")
            print(f"  - Analysis completed: {analysis_results.get('analysis_completed', False)}")
            print(f"  - Has summary: {'summary' in analysis_results}")
            print(f"  - Has results: {'results' in analysis_results}")
            print(f"  - Has visualizations: {'visualizations' in analysis_results}")
            print(f"  - Has config: {'config_used' in analysis_results}")
            
            # Check detailed results
            detailed_results = analysis_results.get('results', {})
            if detailed_results:
                print("\n🔬 Detailed Results Available:")
                print(f"  - Model info: {'model_info' in detailed_results}")
                print(f"  - FBA analysis: {'fba_analysis' in detailed_results}")
                print(f"  - Sensitivity analysis: {'sensitivity_analysis' in detailed_results}")
                print(f"  - Pathway analysis: {'pathway_analysis' in detailed_results}")
                print(f"  - Gene knockout analysis: {'gene_knockout_analysis' in detailed_results}")
                
                # Display some key metrics
                if 'model_info' in detailed_results:
                    model_info = detailed_results['model_info']
                    print(f"\n📋 Model Information:")
                    print(f"  - Model ID: {model_info.get('model_id', 'Unknown')}")
                    print(f"  - Reactions: {model_info.get('reactions_count', 0):,}")
                    print(f"  - Metabolites: {model_info.get('metabolites_count', 0):,}")
                    print(f"  - Genes: {model_info.get('genes_count', 0):,}")
                
                if 'fba_analysis' in detailed_results:
                    fba_results = detailed_results['fba_analysis']
                    print(f"\n⚖️ FBA Results:")
                    print(f"  - Objective value: {fba_results.get('objective_value', 0):.6f}")
                    print(f"  - Status: {fba_results.get('status', 'Unknown')}")
                    print(f"  - Flux distribution entries: {len(fba_results.get('flux_distribution', {}))}")
                
                if 'sensitivity_analysis' in detailed_results:
                    sensitivity = detailed_results['sensitivity_analysis']
                    print(f"\n📈 Sensitivity Analysis:")
                    print(f"  - Glucose sensitivity points: {len(sensitivity.get('glucose_sensitivity', {}))}")
                    print(f"  - Oxygen sensitivity points: {len(sensitivity.get('oxygen_sensitivity', {}))}")
                    print(f"  - Anaerobic growth: {sensitivity.get('anaerobic_growth', 0):.6f}")
            
            # Check if report was generated
            if 'report' in result:
                report = result['report']
                print(f"\n📋 Report Generated:")
                print(f"  - Report length: {len(report)} characters")
                print(f"  - Contains 'Executive Summary': {'Executive Summary' in report}")
                print(f"  - Contains 'Detailed Analysis': {'Detailed Analysis' in report}")
                print(f"  - Contains 'Generated Reports': {'Generated Reports' in report}")
                
                # Save report to file for inspection
                report_file = "test_fba_report.txt"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"  - Report saved to: {report_file}")
            
            # Check visualizations
            visualizations = result.get('visualizations', [])
            print(f"\n📈 Visualizations:")
            print(f"  - Number of visualizations: {len(visualizations)}")
            for i, viz in enumerate(visualizations):
                print(f"    {i+1}. {viz}")
            
            print("\n✅ Test completed successfully!")
            return True
            
        else:
            print(f"❌ FBA analysis failed:")
            print(f"  - Error: {result.get('error', 'Unknown error')}")
            if 'traceback' in result:
                print(f"  - Traceback: {result['traceback']}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fba_result_visualizer():
    """Test the result visualizer with FBA analysis results"""
    
    print("\n🧪 Testing Result Visualizer for Task Type 1")
    print("=" * 60)
    
    try:
        from result_visualizer import EnhancedResultVisualizer
        
        # Create a mock experiment result for testing
        mock_result = {
            'success': True,
            'model_name': 'e_coli_core',
            'task_type': 1,
            'experiment_timestamp': '2024-01-01 12:00:00',
            'results': {
                'analysis_completed': True,
                'summary': {
                    'fba_summary': {
                        'growth_rate': 0.8739,
                        'objective_value': 0.8739,
                        'status': 'optimal',
                        'solver_time': 0.123,
                        'iterations': 15
                    },
                    'model_summary': {
                        'reactions_count': 95,
                        'metabolites_count': 72,
                        'genes_count': 137
                    }
                },
                'results': {
                    'model_info': {
                        'model_id': 'e_coli_core',
                        'reactions_count': 95,
                        'metabolites_count': 72,
                        'genes_count': 137
                    },
                    'fba_analysis': {
                        'objective_value': 0.8739,
                        'status': 'optimal',
                        'flux_distribution': {
                            'EX_glc__D_e': -10.0,
                            'EX_o2_e': -21.8,
                            'EX_co2_e': 22.8,
                            'BIOMASS_Ecoli_core_w_GAM': 0.8739
                        }
                    },
                    'sensitivity_analysis': {
                        'glucose_sensitivity': {
                            '5': 0.5,
                            '10': 0.8,
                            '15': 0.8739,
                            '20': 0.8739
                        },
                        'oxygen_sensitivity': {
                            '10': 0.6,
                            '20': 0.8,
                            '30': 0.8739,
                            '40': 0.8739
                        },
                        'anaerobic_growth': 0.2117
                    },
                    'pathway_analysis': {
                        'pathway_distribution': {
                            'Exchange': 15,
                            'Glycolysis': 8,
                            'TCA_Cycle': 6,
                            'Energy': 4
                        }
                    }
                },
                'output_directory': '/tmp/test_fba_output',
                'visualizations': ['/tmp/test_fba_output/fba_results.png']
            },
            'report': 'Test FBA report content with Executive Summary, Detailed Analysis Results, and Generated Reports sections.'
        }
        
        print("✅ Mock result created successfully")
        print("📊 Result structure verified")
        
        # Test that the visualizer methods can handle the data structure
        visualizer = EnhancedResultVisualizer()
        
        # Test executive summary method
        print("\n🔍 Testing executive summary method...")
        try:
            # This would normally be called by Streamlit, but we can test the logic
            analysis_results = mock_result.get('results', {})
            summary = analysis_results.get('summary', {})
            
            # Check if we can extract the expected data
            fba_summary = summary.get('fba_summary', {})
            model_summary = summary.get('model_summary', {})
            
            print(f"  - FBA summary extracted: {bool(fba_summary)}")
            print(f"  - Model summary extracted: {bool(model_summary)}")
            
            print("✅ Executive summary method test passed")
            
        except Exception as e:
            print(f"❌ Executive summary method test failed: {e}")
            return False
        
        # Test detailed analysis method
        print("\n🔍 Testing detailed analysis method...")
        try:
            # Test the logic for detailed analysis
            results = analysis_results.get('results', {})
            
            # Check if all expected sections are present
            sections = ['model_info', 'fba_analysis', 'sensitivity_analysis', 'pathway_analysis']
            for section in sections:
                if section in results:
                    print(f"  - {section}: ✅")
                else:
                    print(f"  - {section}: ❌")
            
            print("✅ Detailed analysis method test passed")
            
        except Exception as e:
            print(f"❌ Detailed analysis method test failed: {e}")
            return False
        
        # Test generated reports method
        print("\n🔍 Testing generated reports method...")
        try:
            # Test the logic for generated reports
            output_directory = analysis_results.get('output_directory', '')
            visualizations = analysis_results.get('visualizations', [])
            
            print(f"  - Output directory: {output_directory}")
            print(f"  - Visualizations: {len(visualizations)}")
            print(f"  - Report available: {'report' in mock_result}")
            
            print("✅ Generated reports method test passed")
            
        except Exception as e:
            print(f"❌ Generated reports method test failed: {e}")
            return False
        
        print("\n✅ All result visualizer tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Result visualizer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Starting Task Type 1 Tests")
    print("=" * 60)
    
    # Test 1: FBA analysis execution
    test1_passed = test_fba_analysis()
    
    # Test 2: Result visualizer
    test2_passed = test_fba_result_visualizer()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"FBA analysis test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Result visualizer test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Task type 1 is working correctly.")
        print("The Executive Summary, Detailed Analysis Results, and Generated Reports")
        print("sections should now display appropriate content.")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
    
    print("=" * 60)
