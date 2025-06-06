📋 MANUAL TESTING CHECKLIST - SUBSCRIPTION BUTTONS
===============================================

## SETUP ✅ (ALREADY COMPLETED)
- ✅ Flask app running on http://127.0.0.1:5006
- ✅ Test user created: test@example.com / password123
- ✅ JavaScript functions fixed in profile.html
- ✅ Template syntax errors resolved

## YOUR TESTING STEPS 🔍

### **Step 1: Login to the Application**
1. **Open your web browser** (Chrome, Firefox, Safari, etc.)
2. **Navigate to:** http://127.0.0.1:5006/login
3. **Enter credentials:**
   - Email: `test@example.com`
   - Password: `password123`
4. **Click "Login"**
5. **Verify:** You should be redirected to a dashboard or profile page

### **Step 2: Access the Profile Page**
1. **Navigate to:** http://127.0.0.1:5006/profile
   - OR try: http://127.0.0.1:5006/my-account
2. **Look for subscription-related buttons:**
   - "Upgrade to Pro"
   - "Upgrade to Premium" 
   - "Downgrade Plan"
   - "Cancel Subscription"

### **Step 3: Open Browser Developer Tools**
1. **Press F12** (or right-click → "Inspect Element")
2. **Click the "Console" tab**
3. **Clear any existing messages** (click the 🚫 clear button)

### **Step 4: Test the Subscription Buttons**
1. **Click each subscription button** one by one
2. **Watch the Console tab** for any error messages
3. **Expected behavior:**
   - ✅ **NO** "ReferenceError: Can't find variable: upgradePlan" errors
   - ✅ Console may show function execution logs
   - ✅ Modal dialogs or confirmation popups may appear
   - ✅ Buttons should respond without JavaScript errors

### **Step 5: Verify the Fix**
✅ **SUCCESS** if you see:
- No "ReferenceError" messages in console
- Buttons are clickable and responsive
- JavaScript functions execute without errors

❌ **STILL BROKEN** if you see:
- "ReferenceError: Can't find variable: upgradePlan"
- "ReferenceError: Can't find variable: downgradePlan"
- Buttons don't respond when clicked

## TROUBLESHOOTING 🔧

### **If you can't log in:**
- Verify Flask app is still running (check terminal)
- Try refreshing the login page
- Double-check credentials: test@example.com / password123

### **If profile page redirects to login:**
- Sessions may have expired
- Try logging in again
- Clear browser cookies for localhost:5006

### **If you still see JavaScript errors:**
- Take a screenshot of the browser console
- Note the exact error message
- Check if functions are defined by typing in console: `window.upgradePlan`

## REPORT YOUR RESULTS 📊

**Please let me know:**
1. ✅ or ❌ Can you login successfully?
2. ✅ or ❌ Can you access the profile page?
3. ✅ or ❌ Do you see subscription buttons?
4. ✅ or ❌ Do buttons work without "ReferenceError"?
5. Any error messages you see in the browser console

## EXPECTED OUTCOME 🎯

**BEFORE the fix:** "ReferenceError: Can't find variable: upgradePlan"
**AFTER the fix:** Buttons work normally without JavaScript errors

---
⏰ **Next:** Complete this manual testing to verify the fix is working!
