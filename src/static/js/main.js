// Main JavaScript file for Mutual Fund Analyzer

document.addEventListener('DOMContentLoaded', function() {
    // Check if cache status indicator exists on the page
    const cacheIndicator = document.getElementById('cacheIndicator');
    if (cacheIndicator) {
        updateCacheStatus();
    }
    
    // Function to update cache status indicator
    function updateCacheStatus() {
        fetch('/api/cache/status')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    if (data.cache_exists) {
                        const timestamp = new Date(data.timestamp);
                        const now = new Date();
                        const diffHours = Math.abs(now - timestamp) / 36e5; // hours
                        
                        let statusClass = 'bg-success';
                        let statusText = 'Fresh';
                        
                        if (diffHours > 12) {
                            statusClass = 'bg-warning text-dark';
                            statusText = 'Aging';
                        }
                        
                        cacheIndicator.innerHTML = `
                            <span class="badge ${statusClass}">
                                <i class="fas fa-database me-1"></i>${statusText}
                            </span>
                        `;
                    } else {
                        cacheIndicator.innerHTML = `
                            <span class="badge bg-danger">
                                <i class="fas fa-exclamation-circle me-1"></i>No Cache
                            </span>
                        `;
                    }
                }
            })
            .catch(error => {
                console.error('Error checking cache status:', error);
                cacheIndicator.innerHTML = `
                    <span class="badge bg-secondary">
                        <i class="fas fa-question-circle me-1"></i>Unknown
                    </span>
                `;
            });
    }
    
    // Format numbers with commas for thousands
    window.formatNumber = function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
    
    // Format percentage values
    window.formatPercent = function(num) {
        if (num === null || isNaN(num)) return 'N/A';
        return num.toFixed(2) + '%';
    }
    
    // Handle errors in fetch requests
    window.handleFetchError = function(error, elementId, message) {
        console.error('Error:', error);
        document.getElementById(elementId).innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>${message || 'An error occurred. Please try again.'}
            </div>
        `;
    }
});
