// Add country to the countries textarea
function addCountry(countryName) {
    const textarea = document.getElementById('countries');
    if (textarea) {
        const currentValue = textarea.value.trim();
        const countries = currentValue.split('\n').map(c => c.trim()).filter(c => c);
        
        // Check if country already exists
        if (countries.includes(countryName)) {
            alert(`${countryName} is already in the list`);
            return;
        }
        
        // Add country
        countries.push(countryName);
        textarea.value = countries.join('\n');
        
        // Visual feedback
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓ Added';
        btn.style.backgroundColor = '#52c41a';
        btn.style.color = 'white';
        btn.style.borderColor = '#52c41a';
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.backgroundColor = '';
            btn.style.color = '';
            btn.style.borderColor = '';
        }, 1000);
    }
}

// Auto-hide alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

// Confirm service restart
document.addEventListener('DOMContentLoaded', function() {
    const restartForms = document.querySelectorAll('form[action*="service/restart"]');
    restartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to restart the BirdFM service? This will briefly interrupt playback.')) {
                e.preventDefault();
            }
        });
    });
});

// Refresh status indicator periodically
function updateServiceStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            const statusIndicator = document.querySelector('.status-indicator');
            if (statusIndicator) {
                statusIndicator.className = `status-indicator status-${data.status}`;
                const statusText = statusIndicator.querySelector('.status-text');
                if (statusText) {
                    statusText.textContent = data.status;
                }
            }
        })
        .catch(error => console.error('Error updating status:', error));
}

// Update status every 10 seconds on dashboard
if (window.location.pathname === '/' || window.location.pathname === '') {
    setInterval(updateServiceStatus, 10000);
}

// Reboot system function
function rebootSystem() {
    if (!confirm('Are you sure you want to reboot the Raspberry Pi?\n\nThe system will be unavailable for about 30-60 seconds.')) {
        return;
    }
    
    // Show loading message
    const btn = event.target;
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Rebooting...';
    
    fetch('/system/reboot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Show success message
            alert('System is rebooting. The page will automatically refresh in 60 seconds.\n\nPlease wait...');
            
            // Try to reconnect after 60 seconds
            setTimeout(() => {
                window.location.reload();
            }, 60000);
        } else {
            alert('Error: ' + data.message);
            btn.disabled = false;
            btn.textContent = originalText;
        }
    })
    .catch(error => {
        console.error('Reboot request sent, system is likely rebooting');
        alert('Reboot initiated. The page will automatically refresh in 60 seconds.\n\nPlease wait...');
        
        // Try to reconnect after 60 seconds
        setTimeout(() => {
            window.location.reload();
        }, 60000);
    });
}
