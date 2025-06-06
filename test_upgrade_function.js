// Test file to verify upgradePlan function works
console.log('Testing upgradePlan function...');

// Mock DOM functions for testing
function createConfirmationModal(title, message, confirmText, cancelText, onConfirm) {
    console.log('Modal would show:', title, message);
    // Simulate user clicking confirm
    setTimeout(() => {
        console.log('User confirmed, calling onConfirm...');
        onConfirm();
    }, 100);
    return { style: { display: 'flex' }, querySelector: () => null };
}

// Mock DOM elements
global.document = {
    createElement: (tag) => ({
        method: '',
        action: '',
        appendChild: () => {},
        submit: () => console.log('Form submitted'),
        addEventListener: () => {}
    }),
    body: {
        appendChild: () => {}
    },
    querySelectorAll: () => [],
    head: {
        appendChild: () => {}
    }
};

// The actual upgradePlan function from profile.html
function upgradePlan(plan) {
    console.log('Attempting to upgrade to ' + plan + ' plan');
    
    // Validate plan
    if (!plan || !['Pro', 'Premium'].includes(plan)) {
        console.log('Invalid plan selected. Please try again.');
        return;
    }
    
    const confirmMessage = 'Are you sure you want to upgrade to the ' + plan + ' plan?';
    const modal = createConfirmationModal(
        'Upgrade Subscription',
        confirmMessage,
        'Upgrade',
        'Cancel',
        function() {
            console.log('User confirmed upgrade, submitting form...');
            
            // Show loading state
            const upgradeButtons = document.querySelectorAll('.select-plan-btn.upgrade');
            upgradeButtons.forEach(btn => {
                btn.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Processing...';
                btn.disabled = true;
            });
            
            // Create and submit form with error handling
            try {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '/create-checkout-session';
                
                const planInput = document.createElement('input');
                planInput.type = 'hidden';
                planInput.name = 'plan';
                planInput.value = plan;
                
                form.appendChild(planInput);
                document.body.appendChild(form);
                
                // Add form submit listener for debugging
                form.addEventListener('submit', function() {
                    console.log('Form submitted for plan:', plan);
                });
                
                form.submit();
            } catch (error) {
                console.error('Error creating upgrade form:', error);
                console.log('An error occurred. Please refresh the page and try again.');
                // Reset button state
                upgradeButtons.forEach(btn => {
                    btn.innerHTML = 'Upgrade to ' + plan;
                    btn.disabled = false;
                });
            }
        }
    );
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
    
    // Focus the modal for accessibility
    setTimeout(() => {
        const confirmBtn = modal.querySelector('.btn-primary');
        if (confirmBtn) confirmBtn.focus();
    }, 100);
}

// Test the function
console.log('=== Testing upgradePlan function ===');
upgradePlan('Pro');

setTimeout(() => {
    console.log('=== Testing upgradePlan function with Premium ===');
    upgradePlan('Premium');
}, 500);

setTimeout(() => {
    console.log('=== Testing upgradePlan function with invalid plan ===');
    upgradePlan('Invalid');
}, 1000);
