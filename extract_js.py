#!/usr/bin/env python3
"""
Extract JavaScript from profile.html and save it as a separate file for testing
"""

import re

def extract_javascript(template_path, output_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the script block
    script_start = content.find('<script>')
    script_end = content.find('</script>')
    
    if script_start == -1 or script_end == -1:
        print("❌ Script tags not found")
        return False
    
    # Extract JavaScript content
    js_content = content[script_start + 8:script_end]  # +8 for '<script>'
    
    print(f"✅ Extracted {len(js_content)} characters of JavaScript")
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✅ Saved JavaScript to {output_path}")
    return True

def main():
    template_path = '/Users/sevs/Documents/Programs/webapps/resume_builder/templates/profile.html'
    output_path = '/Users/sevs/Documents/Programs/webapps/resume_builder/extracted_profile.js'
    
    print(f"🔍 Extracting JavaScript from {template_path}")
    
    if extract_javascript(template_path, output_path):
        print("\n🔍 Now checking syntax with Node.js...")
        import subprocess
        try:
            result = subprocess.run(['node', '-c', output_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ JavaScript syntax is valid!")
            else:
                print("❌ JavaScript syntax error:")
                print(result.stderr)
        except FileNotFoundError:
            print("⚠️ Node.js not found, cannot check syntax")
    else:
        print("❌ Failed to extract JavaScript")

if __name__ == "__main__":
    main()
