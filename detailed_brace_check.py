#!/usr/bin/env python3
"""
Detailed JavaScript brace checker for upgradePlan function
"""

def check_braces_in_function(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the upgradePlan function
    start_marker = 'function upgradePlan(plan) {'
    start_index = content.find(start_marker)
    
    if start_index == -1:
        # Try alternative format
        start_marker = 'function upgradePlan('
        start_index = content.find(start_marker)
        if start_index == -1:
            print("❌ upgradePlan function not found")
            return
        # Find the opening brace after the function signature
        brace_start = content.find('{', start_index)
        if brace_start == -1:
            print("❌ Opening brace not found")
            return
    else:
        brace_start = start_index + len(start_marker) - 1
    brace_count = 0
    line_num = content[:start_index].count('\n') + 1
    
    i = brace_start
    while i < len(content):
        char = content[i]
        
        if char == '\n':
            line_num += 1
        elif char == '{':
            brace_count += 1
            print(f"Line {line_num}: Opening brace {{ (count: {brace_count})")
        elif char == '}':
            brace_count -= 1
            print(f"Line {line_num}: Closing brace }} (count: {brace_count})")
            
            # If we've closed all braces, this is the end of the function
            if brace_count == 0:
                print(f"✅ Function ends at line {line_num}, position {i}")
                print(f"Function content length: {i - brace_start + 1} characters")
                
                # Check if the next non-whitespace character is what we expect
                next_content = content[i+1:i+100].strip()
                print(f"Next content after function: {next_content[:50]}...")
                return
        
        i += 1
    
    if brace_count != 0:
        print(f"❌ Unmatched braces! Final count: {brace_count}")
        print("This means there are missing closing braces")
    
def main():
    template_path = '/Users/sevs/Documents/Programs/webapps/resume_builder/templates/profile.html'
    check_braces_in_function(template_path)

if __name__ == "__main__":
    main()
