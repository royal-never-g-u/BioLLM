#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysis trigger script
"""

import subprocess
import sys
import os

def main():
    """Run the analysis script"""
    script_path = "/Users/wjgy/PycharmProjects/BioLLM/BioLLM/Temp/e_coli_core_analysis_script.py"
    
    if os.path.exists(script_path):
        print(f"🔬 Running analysis script: {script_path}")
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            print("📋 Analysis Results:")
            print("=" * 50)
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Errors/Warnings:")
                print(result.stderr)
                
        except subprocess.TimeoutExpired:
            print("⏰ Analysis timed out after 5 minutes")
        except Exception as e:
            print(f"❌ Error running analysis: {e}")
    else:
        print(f"❌ Analysis script not found: {script_path}")

if __name__ == "__main__":
    main()
