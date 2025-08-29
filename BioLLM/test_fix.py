#!/usr/bin/env python3
"""
Test script to verify the fix for FBA and Constraint-Based Analysis
"""

import os
import sys
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_bio_task_setup():
    """Test setting up bio_task for testing"""
    from bio_task import update_current_task
    
    # Test with task type 1 (FBA)
    update_current_task("e_coli_core", "/tmp/test_model.mat", 1)
    
    print("✅ bio_task setup completed")

def test_fba_execution():
    """Test FBA execution"""
    from experiment_executor import execute_experiment
    
    print("\n🔬 Testing FBA execution...")
    
    # Execute FBA analysis
    result = execute_experiment("e_coli_core", 1)
    
    if result.get('success', False):
        print("✅ FBA execution successful")
        
        # Check if visualizations are properly extracted
        visualizations = result.get('visualizations', [])
        print(f"📊 Found {len(visualizations)} visualization files")
        
        for i, viz_path in enumerate(visualizations):
            print(f"  {i+1}. {viz_path}")
            if os.path.exists(viz_path):
                print(f"     ✅ File exists")
            else:
                print(f"     ❌ File not found")
        
        # Check if analysis results are available
        results = result.get('results', {})
        if results:
            analysis_results = results.get('results', {})
            if analysis_results:
                data_files = analysis_results.get('data_files', {})
                if 'analysis_results.json' in data_files:
                    print("✅ analysis_results.json found")
                    model_info = data_files['analysis_results.json']
                    if isinstance(model_info, dict):
                        print("✅ analysis_results.json is properly loaded")
                        print(f"   Model info: {model_info.get('model_info', {})}")
                        print(f"   FBA analysis: {bool(model_info.get('fba_analysis', {}))}")
                        print(f"   Sensitivity analysis: {bool(model_info.get('sensitivity_analysis', {}))}")
                    else:
                        print("❌ analysis_results.json is not a dict")
                else:
                    print("❌ analysis_results.json not found")
            else:
                print("❌ No analysis_results in results")
        else:
            print("❌ No results found")
    else:
        print(f"❌ FBA execution failed: {result.get('error', 'Unknown error')}")
    
    return result

def test_constraint_based_execution():
    """Test Constraint-Based Analysis execution"""
    from experiment_executor import execute_experiment
    
    print("\n🔬 Testing Constraint-Based Analysis execution...")
    
    # Execute Constraint-Based Analysis
    result = execute_experiment("e_coli_core", 6)
    
    if result.get('success', False):
        print("✅ Constraint-Based Analysis execution successful")
        
        # Check if visualizations are properly extracted
        visualizations = result.get('visualizations', [])
        print(f"📊 Found {len(visualizations)} visualization files")
        
        for i, viz_path in enumerate(visualizations):
            print(f"  {i+1}. {viz_path}")
            if os.path.exists(viz_path):
                print(f"     ✅ File exists")
            else:
                print(f"     ❌ File not found")
        
        # Check if analysis results are available
        results = result.get('results', {})
        if results:
            analysis_results = results.get('results', {})
            if analysis_results:
                data_files = analysis_results.get('data_files', {})
                if 'analysis_results.json' in data_files:
                    print("✅ analysis_results.json found")
                    model_info = data_files['analysis_results.json']
                    if isinstance(model_info, dict):
                        print("✅ analysis_results.json is properly loaded")
                        print(f"   Basic info: {bool(model_info.get('basic_info', {}))}")
                        print(f"   FBA analysis: {bool(model_info.get('fba_analysis', {}))}")
                        print(f"   Growth analysis: {bool(model_info.get('growth_analysis', {}))}")
                        print(f"   Environmental analysis: {bool(model_info.get('environmental_analysis', {}))}")
                    else:
                        print("❌ analysis_results.json is not a dict")
                else:
                    print("❌ analysis_results.json not found")
            else:
                print("❌ No analysis_results in results")
        else:
            print("❌ No results found")
    else:
        print(f"❌ Constraint-Based Analysis execution failed: {result.get('error', 'Unknown error')}")
    
    return result

def main():
    """Main test function"""
    print("🧪 Testing FBA and Constraint-Based Analysis Fix")
    print("=" * 60)
    
    # Test bio_task setup
    test_bio_task_setup()
    
    # Test FBA execution
    fba_result = test_fba_execution()
    
    # Test Constraint-Based Analysis execution
    cba_result = test_constraint_based_execution()
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"FBA Analysis: {'✅ PASS' if fba_result.get('success', False) else '❌ FAIL'}")
    print(f"Constraint-Based Analysis: {'✅ PASS' if cba_result.get('success', False) else '❌ FAIL'}")
    
    if fba_result.get('success', False) and cba_result.get('success', False):
        print("\n🎉 All tests passed! The fix is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
