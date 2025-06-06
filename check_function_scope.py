#!/usr/bin/env python3
"""
Find the scope of DOMContentLoaded listener and upgradePlan function
"""

def analyze_function_scope():
    with open('/Users/sevs/Documents/Programs/webapps/resume_builder/templates/profile.html', 'r') as f:
        content = f.read()
    
    # Find DOMContentLoaded start
    dom_start = content.find('window.addEventListener(\'DOMContentLoaded\', function() {')
    if dom_start == -1:
        print("❌ DOMContentLoaded not found")
        return
    
    print(f"✅ DOMContentLoaded starts at position {dom_start}")
    
    # Find the corresponding closing brace
    brace_count = 0
    in_listener = False
    dom_end = len(content)  # Default to end of file
    
    for i, char in enumerate(content[dom_start:]):
        if char == '{':
            brace_count += 1
            in_listener = True
        elif char == '}' and in_listener:
            brace_count -= 1
            if brace_count == 0:
                dom_end = dom_start + i
                print(f"✅ DOMContentLoaded ends at position {dom_end}")
                break
    else:
        print("⚠️ Could not find end of DOMContentLoaded - checking manually")
    
    # Find upgradePlan function
    upgrade_start = content.find('function upgradePlan(plan) {')
    if upgrade_start == -1:
        print("❌ upgradePlan function not found")
        return False
    
    print(f"✅ upgradePlan function starts at position {upgrade_start}")
    
    # Convert positions to line numbers for easier understanding
    dom_start_line = content[:dom_start].count('\n') + 1
    dom_end_line = content[:dom_end].count('\n') + 1
    upgrade_line = content[:upgrade_start].count('\n') + 1
    
    print(f"DOMContentLoaded: lines {dom_start_line} to {dom_end_line}")
    print(f"upgradePlan function: line {upgrade_line}")
    
    # Check if upgradePlan is inside DOMContentLoaded
    if dom_start < upgrade_start < dom_end:
        print("❌ PROBLEM: upgradePlan function is INSIDE DOMContentLoaded listener!")
        print("   This makes it inaccessible to onclick handlers")
        
        # Show some context
        context_start = max(0, upgrade_start - 200)
        context_end = min(len(content), upgrade_start + 200)
        context = content[context_start:context_end]
        print("Context around upgradePlan function:")
        print("=" * 50)
        print(context)
        print("=" * 50)
        
        return False
    else:
        print("✅ upgradePlan function is OUTSIDE DOMContentLoaded listener")
        return True

if __name__ == "__main__":
    analyze_function_scope()
