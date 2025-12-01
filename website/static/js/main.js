/**
 * Bioworld Website - Main JavaScript
 * Handles API health check and common functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check API health status
    checkApiHealth();
});

/**
 * Check the API health endpoint and update status indicator
 */
async function checkApiHealth() {
    const healthIndicator = document.getElementById('api-health');
    if (!healthIndicator) return;

    const statusDot = healthIndicator.querySelector('.status-dot');
    const statusText = healthIndicator.querySelector('.status-text');

    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        if (data.status === 'healthy') {
            statusDot.classList.remove('error');
            statusDot.classList.add('healthy');
            statusText.textContent = `Healthy (v${data.version})`;
        } else {
            statusDot.classList.remove('healthy');
            statusDot.classList.add('error');
            statusText.textContent = 'Degraded';
        }
    } catch (error) {
        statusDot.classList.remove('healthy');
        statusDot.classList.add('error');
        statusText.textContent = 'Offline';
        console.error('API health check failed:', error);
    }
}

/**
 * Format a date string for display
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - 'success', 'error', or 'info'
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background-color: ${type === 'success' ? '#30d158' : type === 'error' ? '#ff6b6b' : '#0a84ff'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
