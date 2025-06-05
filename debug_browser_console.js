console.log("=== JavaScript Function Check ===");
console.log("Checking if subscription button functions are defined...");

// Check if functions exist
const functions = ['upgradePlan', 'downgradePlan', 'createConfirmationModal'];

functions.forEach(funcName => {
    if (typeof window[funcName] === 'function') {
        console.log(`✅ ${funcName}: DEFINED`);
    } else {
        console.log(`❌ ${funcName}: NOT DEFINED`);
        console.log(`   Type: ${typeof window[funcName]}`);
    }
});

// Check all script tags
const scripts = document.querySelectorAll('script');
console.log(`\nFound ${scripts.length} script tags:`);
scripts.forEach((script, index) => {
    if (script.innerHTML.includes('upgradePlan')) {
        console.log(`✅ Script ${index + 1}: Contains upgradePlan function`);
    }
});

// Check for any JavaScript errors
console.log("\n=== Instructions ===");
console.log("1. Copy this code");
console.log("2. Open your browser's Developer Tools (F12)");
console.log("3. Go to the Console tab");
console.log("4. Paste this code and press Enter");
console.log("5. Check the output to see if functions are defined");

// Test button click simulation
setTimeout(() => {
    const proButton = document.querySelector('button[onclick*="upgradePlan"]');
    if (proButton) {
        console.log("✅ Found subscription button with onclick handler");
        console.log("Button text:", proButton.textContent.trim());
    } else {
        console.log("❌ No subscription button found");
    }
}, 1000);
