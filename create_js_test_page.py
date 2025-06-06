#!/usr/bin/env python3
"""
Create a standalone test page with the exact JavaScript from profile.html
"""

import requests

def create_test_page():
    print("🔧 Creating standalone test page...")
    
    # Get the JavaScript from the profile page
    session = requests.Session()
    login_data = {'email': 'debug@test.com', 'password': 'testpassword123'}
    session.post('http://127.0.0.1:5006/login', data=login_data)
    
    profile_response = session.get('http://127.0.0.1:5006/profile')
    html = profile_response.text
    
    # Extract JavaScript between <script> and </script>
    start_marker = '<script>'
    end_marker = '</script>'
    
    start_idx = html.find(start_marker)
    end_idx = html.find(end_marker, start_idx)
    
    if start_idx != -1 and end_idx != -1:
        js_content = html[start_idx + len(start_marker):end_idx]
        print(f"✅ Extracted {len(js_content)} characters of JavaScript")
        
        # Create a test HTML page
        test_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subscription Button Test</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        .test-container {{
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }}
        .select-plan-btn {{
            padding: 10px 20px;
            margin: 10px;
            border: 2px solid #007bff;
            background: #007bff;
            color: white;
            border-radius: 5px;
            cursor: pointer;
        }}
        .select-plan-btn:hover {{
            background: #0056b3;
        }}
        .test-output {{
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
            min-height: 100px;
        }}
    </style>
</head>
<body>
    <div class="test-container">
        <h1>Subscription Button Test</h1>
        <p>This page tests the subscription JavaScript functions isolated from the main application.</p>
        
        <div class="mb-3">
            <h3>Test Buttons:</h3>
            <button class="select-plan-btn upgrade" onclick="try {{ console.log('Pro button clicked'); upgradePlan('Pro'); }} catch(e) {{ console.error('Error calling upgradePlan:', e); alert('Error: ' + e.message); }}">
                Upgrade to Pro
            </button>
            
            <button class="select-plan-btn upgrade" onclick="try {{ console.log('Premium button clicked'); upgradePlan('Premium'); }} catch(e) {{ console.error('Error calling upgradePlan:', e); alert('Error: ' + e.message); }}">
                Upgrade to Premium
            </button>
        </div>
        
        <div class="mb-3">
            <h3>Direct Function Tests:</h3>
            <button onclick="testFunctionAvailability()" class="btn btn-info">Check Function Availability</button>
            <button onclick="testDirectCall()" class="btn btn-success">Test Direct Call</button>
        </div>
        
        <div class="test-output" id="testOutput">
            <strong>Test Output:</strong><br>
            <span id="outputText">Click buttons to test functionality...</span>
        </div>
    </div>

    <script>
        // Add test helper functions
        function logOutput(message) {{
            console.log(message);
            const output = document.getElementById('outputText');
            output.innerHTML += '<br>' + message;
        }}
        
        function testFunctionAvailability() {{
            logOutput('=== Testing Function Availability ===');
            logOutput('typeof window.upgradePlan: ' + typeof window.upgradePlan);
            logOutput('typeof window.downgradePlan: ' + typeof window.downgradePlan);
            logOutput('typeof window.createConfirmationModal: ' + typeof window.createConfirmationModal);
            
            if (typeof window.upgradePlan === 'function') {{
                logOutput('✅ upgradePlan is available');
            }} else {{
                logOutput('❌ upgradePlan is NOT available');
            }}
        }}
        
        function testDirectCall() {{
            logOutput('=== Testing Direct Function Call ===');
            try {{
                if (typeof window.upgradePlan === 'function') {{
                    logOutput('Calling upgradePlan("Test")...');
                    window.upgradePlan('Test');
                    logOutput('✅ Function call completed');
                }} else {{
                    logOutput('❌ Function not available for direct call');
                }}
            }} catch (error) {{
                logOutput('❌ Error in direct call: ' + error.message);
                console.error('Direct call error:', error);
            }}
        }}
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            logOutput('Page loaded. Initializing...');
            
            // Test immediately after a short delay
            setTimeout(function() {{
                testFunctionAvailability();
            }}, 500);
        }});
        
        {js_content}
    </script>
</body>
</html>"""
        
        # Save the test page
        with open('/Users/sevs/Documents/Programs/webapps/resume_builder/subscription_test.html', 'w') as f:
            f.write(test_html)
        
        print("✅ Test page created: subscription_test.html")
        return True
        
    else:
        print("❌ Could not extract JavaScript from profile page")
        return False

if __name__ == "__main__":
    if create_test_page():
        print("🌐 Open the test page in your browser:")
        print("file:///Users/sevs/Documents/Programs/webapps/resume_builder/subscription_test.html")
        print("Check the browser console for debug messages")
    else:
        print("❌ Failed to create test page")
