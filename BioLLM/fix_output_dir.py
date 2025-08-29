#!/usr/bin/env python3
"""
Fix OUTPUT_DIR replacement in experiment_executor.py
"""

def fix_output_dir_replacement():
    """Fix the OUTPUT_DIR replacement in experiment_executor.py"""
    
    # Read the file
    with open('experiment_executor.py', 'r') as f:
        content = f.read()
    
    # Replace the problematic line
    old_line = "custom_content = custom_content.replace('{{OUTPUT_DIR}}', output_config.get('output_directory', ''))"
    new_line = 'custom_content = custom_content.replace(\'"{{OUTPUT_DIR}}"\', f\'"{output_config.get("output_directory", "")}"\')'
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print(f"✅ Fixed OUTPUT_DIR replacement")
    else:
        print(f"❌ Could not find the line to replace")
        return False
    
    # Write back to file
    with open('experiment_executor.py', 'w') as f:
        f.write(content)
    
    print(f"✅ Updated experiment_executor.py")
    return True

if __name__ == "__main__":
    fix_output_dir_replacement()
