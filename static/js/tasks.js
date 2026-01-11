/**
 * Task Management JavaScript
 * Handles AJAX operations for task completion and UI updates
 */

/**
 * Complete a task via AJAX
 * @param {number} taskId - The ID of the task to complete
 */
function completeTask(taskId) {
    if (!confirm('Mark this task as complete?')) {
        return;
    }
    
    fetch(`/tasks/${taskId}/complete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Show success message
            showFlashMessage(data.message, 'success');
            
            // Reload page to update UI
            setTimeout(() => {
                window.location.reload();
            }, 500);
        } else {
            showFlashMessage(data.error || 'Failed to complete task', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('An error occurred. Please try again.', 'danger');
    });
}

/**
 * Uncomplete (reopen) a task via AJAX
 * @param {number} taskId - The ID of the task to reopen
 */
function uncompleteTask(taskId) {
    if (!confirm('Reopen this task?')) {
        return;
    }
    
    fetch(`/tasks/${taskId}/uncomplete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showFlashMessage(data.message, 'success');
            
            setTimeout(() => {
                window.location.reload();
            }, 500);
        } else {
            showFlashMessage(data.error || 'Failed to reopen task', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('An error occurred. Please try again.', 'danger');
    });
}

/**
 * Show a flash message dynamically
 * @param {string} message - The message to display
 * @param {string} category - The category (success, danger, warning, info)
 */
function showFlashMessage(message, category) {
    // Remove existing flash messages
    const existingMessages = document.querySelector('.flash-messages');
    if (existingMessages) {
        existingMessages.remove();
    }
    
    // Create new flash message
    const flashContainer = document.createElement('div');
    flashContainer.className = 'flash-messages';
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${category}`;
    alert.innerHTML = `
        ${message}
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    flashContainer.appendChild(alert);
    
    // Insert at the top of main content
    const main = document.querySelector('.main .container');
    if (main) {
        main.insertBefore(flashContainer, main.firstChild);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (flashContainer.parentElement) {
            flashContainer.remove();
        }
    }, 5000);
}

/**
 * Initialize tooltips and other UI enhancements
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + N to create new task
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const createLink = document.querySelector('a[href*="/tasks/create"]');
            if (createLink) {
                window.location.href = createLink.href;
            }
        }
    });
    
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Loading...';
            }
        });
    });
    
    // Auto-hide flash messages
    setTimeout(() => {
        const flashMessages = document.querySelectorAll('.alert');
        flashMessages.forEach(msg => {
            msg.style.transition = 'opacity 0.3s';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 300);
        });
    }, 5000);
});
