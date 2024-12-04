// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Handle deletion with confirmation and visual feedback
function handleDelete(url, elementId, type) {
    // Show confirmation dialog
    if (!confirm(`Are you sure you want to delete this ${type}? This action cannot be undone.`)) {
        return;
    }

    // Add loading state
    const element = document.getElementById(elementId);
    const originalContent = element.innerHTML;
    element.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin"></i> Deleting...</div>';
    element.style.opacity = '0.5';

    // Send delete request
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Fade out and remove the element
            element.style.transition = 'opacity 0.5s ease';
            element.style.opacity = '0';
            setTimeout(() => {
                element.remove();
                // Show success message
                showMessage('success', `${type} deleted successfully!`);
                // Update counters if needed
                updateCounters();
            }, 500);
        } else {
            // Show error and restore original content
            element.innerHTML = originalContent;
            element.style.opacity = '1';
            showMessage('error', data.message || `Error deleting ${type}`);
        }
    })
    .catch(error => {
        // Show error and restore original content
        element.innerHTML = originalContent;
        element.style.opacity = '1';
        showMessage('error', `Network error while deleting ${type}`);
        console.error('Error:', error);
    });
}

// Show message function
function showMessage(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to messages container
    const messagesContainer = document.querySelector('.messages');
    if (messagesContainer) {
        messagesContainer.appendChild(alertDiv);
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Update counters function
function updateCounters() {
    // Update category count
    const categoryCount = document.querySelectorAll('.menu-category').length;
    const categoryCounter = document.querySelector('.category-counter');
    if (categoryCounter) {
        categoryCounter.textContent = categoryCount;
    }

    // Update item count
    const itemCount = document.querySelectorAll('.menu-item').length;
    const itemCounter = document.querySelector('.item-counter');
    if (itemCounter) {
        itemCounter.textContent = itemCount;
    }
}

// Initialize tooltips and other Bootstrap components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
