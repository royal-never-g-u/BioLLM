#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug Script for Analyse Command Extension

This script helps debug why cobra visual analysis is not being generated
during the analyse command execution.
"""

import os
import sys
from agent.model_analyzer_agent import ModelAnalyzerAgent

def debug_analyse_extension():
    """Debug the analyse command extension"""
    
    print("="*60)
    print("Debugging Analyse Command Extension")
    print("="*60)
    
    # Test model path
    model_path = "../downloads/e_coli_core.mat"
    
    if not os.path.exists(model_path):
        print(f"❌ Model file not found: {model_path}")
        return False
    
    print(f"✅ Model file found: {model_path}")
    
    # Test 1: Check ModelAnalyzerAgent initialization
    print("\n" + "="*40)
    print("Test 1: ModelAnalyzerAgent Initialization")
    print("="*40)
    
    try:
        agent = ModelAnalyzerAgent()
        print("✅ ModelAnalyzerAgent initialized successfully")
        
        # Check cobra visual agent availability
        print(f"CobraVisualAgent available: {agent.cobra_visual_agent is not None}")
        if agent.cobra_visual_agent:
            print("✅ CobraVisualAgent is available")
        else:
            print("❌ CobraVisualAgent is NOT available")
            print("This is likely the cause of the issue!")
            
    except Exception as e:
        print(f"❌ Error initializing ModelAnalyzerAgent: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Check if cobra visual agent can be imported
    print("\n" + "="*40)
    print("Test 2: CobraVisualAgent Import Test")
    print("="*40)
    
    try:
        from agent.cobra_visual_agent import CobraVisualAgent
        print("✅ CobraVisualAgent can be imported")
        
        # Try to create an instance
        cobra_agent = CobraVisualAgent()
        print("✅ CobraVisualAgent instance created successfully")
        
    except Exception as e:
        print(f"❌ Error with CobraVisualAgent: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Check the _analyze_model method
    print("\n" + "="*40)
    print("Test 3: _analyze_model Method Check")
    print("="*40)
    
    try:
        # Check if the method exists
        if hasattr(agent, '_analyze_model'):
            print("✅ _analyze_model method exists")
        else:
            print("❌ _analyze_model method does not exist")
            return False
        
        # Check if _generate_cobra_visual_analysis method exists
        if hasattr(agent, '_generate_cobra_visual_analysis'):
            print("✅ _generate_cobra_visual_analysis method exists")
        else:
            print("❌ _generate_cobra_visual_analysis method does not exist")
            return False
            
    except Exception as e:
        print(f"❌ Error checking methods: {e}")
        return False
    
    # Test 4: Run a minimal analyse test
    print("\n" + "="*40)
    print("Test 4: Minimal Analyse Test")
    print("="*40)
    
    try:
        # Run the analyse command
        result = agent.run("analyse e_coli_core")
        
        print(f"✅ Analyse command completed")
        print(f"📊 Result length: {len(result)} characters")
        
        # Check for cobra visual results in the text
        if "Cobra Visual Analysis Results" in result:
            print("✅ Cobra visual analysis results found in text output")
        else:
            print("❌ Cobra visual analysis results NOT found in text output")
            print("This indicates the cobra visual analysis was not executed")
        
        # Check for cobra visual files
        cobra_visual_dir = "model_data/e_coli_core/cobra_visual"
        if os.path.exists(cobra_visual_dir):
            print(f"✅ Cobra visual directory exists: {cobra_visual_dir}")
            files = os.listdir(cobra_visual_dir)
            print(f"📁 Files in cobra_visual directory: {len(files)}")
            for file in sorted(files):
                print(f"  📄 {file}")
        else:
            print(f"❌ Cobra visual directory does not exist: {cobra_visual_dir}")
        
        # Check streamlit figures
        if hasattr(agent, 'streamlit_figures') and agent.streamlit_figures:
            print(f"✅ Streamlit figures generated: {len(agent.streamlit_figures)}")
            
            # Check for cobra visual figures
            cobra_figures = [f for f in agent.streamlit_figures 
                           if isinstance(f, dict) and f.get('name', '').startswith('Cobra Visual -')]
            
            if cobra_figures:
                print(f"✅ Cobra visual figures found: {len(cobra_figures)}")
                for fig in cobra_figures:
                    print(f"  🎨 {fig.get('name', 'Unknown')}")
            else:
                print("❌ No cobra visual figures found in streamlit figures")
        else:
            print("❌ No streamlit figures generated")
            
    except Exception as e:
        print(f"❌ Error running analyse command: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Direct cobra visual test
    print("\n" + "="*40)
    print("Test 5: Direct Cobra Visual Test")
    print("="*40)
    
    try:
        if agent.cobra_visual_agent:
            # Test direct cobra visual execution
            cobra_output_dir = "model_data/e_coli_core/cobra_visual_test"
            os.makedirs(cobra_output_dir, exist_ok=True)
            
            request = {
                'model_path': model_path,
                'output_dir': cobra_output_dir,
                'visualization_types': ['network', 'fluxmap', 'analysis'],
                'analysis_level': 'comprehensive'
            }
            
            print("🔄 Testing direct cobra visual execution...")
            result = agent.cobra_visual_agent.process_request(request)
            
            if result['success']:
                print("✅ Direct cobra visual execution successful")
                
                # Check generated files
                if os.path.exists(cobra_output_dir):
                    files = os.listdir(cobra_output_dir)
                    print(f"📁 Generated files: {len(files)}")
                    for file in sorted(files):
                        print(f"  📄 {file}")
                else:
                    print("❌ No output directory created")
            else:
                print(f"❌ Direct cobra visual execution failed: {result.get('error', 'Unknown error')}")
        else:
            print("⚠️ Skipping direct test - CobraVisualAgent not available")
            
    except Exception as e:
        print(f"❌ Error in direct cobra visual test: {e}")
        import traceback
        traceback.print_exc()
    
    return True

def main():
    """Main function"""
    success = debug_analyse_extension()
    
    if success:
        print("\n" + "="*60)
        print("🔍 Debug completed. Check the output above for issues.")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Debug failed. Check the errors above.")
        print("="*60)

if __name__ == "__main__":
    main()
