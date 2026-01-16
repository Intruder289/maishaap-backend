// Dropdown Actions JavaScript
// This file handles all dropdown action functionality across the application

document.addEventListener('DOMContentLoaded', function() {
    // Handle dropdown actions
    document.addEventListener('click', function(e) {
        // Handle toggle status action
        if (e.target.closest('.toggle-status-action')) {
            e.preventDefault();
            e.stopPropagation(); // Prevent dropdown from closing
            const link = e.target.closest('.toggle-status-action');
            const url = link.dataset.url;
            const itemId = link.dataset.itemId;
            
            if (!url || !itemId) {
                console.error('Missing URL or itemId for status action');
                showNotification('Invalid action configuration', 'error');
                return;
            }
            
            if (confirm('Are you sure you want to change the status of this item?')) {
                toggleItemStatus(url, itemId, link);
            }
        }
        
        // Handle toggle approval action
        if (e.target.closest('.toggle-approval-action')) {
            e.preventDefault();
            e.stopPropagation(); // Prevent dropdown from closing
            const link = e.target.closest('.toggle-approval-action');
            const url = link.dataset.url;
            const itemId = link.dataset.itemId;
            
            if (!url || !itemId) {
                console.error('Missing URL or itemId for approval action');
                showNotification('Invalid action configuration', 'error');
                return;
            }
            
            const isApproved = link.textContent.trim().includes('Unapprove');
            const confirmMessage = isApproved 
                ? 'Are you sure you want to unapprove this user? They will not be able to login until approved again.'
                : 'Are you sure you want to approve this user? They will be able to login immediately.';
            
            if (confirm(confirmMessage)) {
                toggleUserApproval(url, itemId, link);
            }
        }
        
        // Handle reset password action
        if (e.target.closest('.reset-password-action')) {
            e.preventDefault();
            e.stopPropagation();
            const link = e.target.closest('.reset-password-action');
            const url = link.dataset.url;
            const itemId = link.dataset.itemId;
            
            if (!url || !itemId) {
                console.error('Missing URL or itemId for reset password action');
                showNotification('Invalid action configuration', 'error');
                return;
            }
            
            if (confirm('Are you sure you want to reset this user\'s password to the default? The new password will be: DefaultPass@12')) {
                resetUserPassword(url, itemId, link);
            }
        }
        
        // Handle delete action
        if (e.target.closest('.delete-action')) {
            e.preventDefault();
            const link = e.target.closest('.delete-action');
            const url = link.dataset.url;
            const itemId = link.dataset.itemId;
            const itemName = link.dataset.itemName;
            
            if (confirm(`Are you sure you want to delete this ${itemName}? This action cannot be undone.`)) {
                deleteItem(url, itemId, link.closest('tr'));
            }
        }
        
        // Handle custom actions with confirmation
        if (e.target.closest('[data-confirm]')) {
            const link = e.target.closest('[data-confirm]');
            const confirmMessage = link.dataset.confirm;
            
            if (!confirm(confirmMessage)) {
                e.preventDefault();
            }
        }
    });
});

function toggleItemStatus(url, itemId, linkElement) {
    console.log('toggleItemStatus called', { url, itemId });
    const csrfToken = getCSRFToken();
    if (!csrfToken) {
        console.error('CSRF token not found');
        showNotification('Security token not found. Please refresh the page.', 'error');
        return;
    }
    
    console.log('Sending status request to:', url);
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || 'Server error');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update the link text and icon
            const icon = linkElement.querySelector('i');
            const text = linkElement.textContent.trim();
            
            if (text.includes('Activate')) {
                icon.className = 'fas fa-toggle-on me-2 text-warning';
                linkElement.innerHTML = '<i class="fas fa-toggle-on me-2 text-warning"></i>Deactivate';
            } else {
                icon.className = 'fas fa-toggle-off me-2 text-success';
                linkElement.innerHTML = '<i class="fas fa-toggle-off me-2 text-success"></i>Activate';
            }
            
            // Update status badge in the row
            const row = linkElement.closest('tr');
            const statusBadge = row.querySelector('td:nth-child(4) .badge'); // Status column
            if (statusBadge && data.new_status) {
                statusBadge.className = `badge ${data.new_status.class}`;
                statusBadge.innerHTML = `<i class="fas fa-${data.is_active ? 'check' : 'times'}-circle me-1"></i>${data.new_status.text}`;
            }
            
            if (data.message) {
                showNotification(data.message, data.status_corrected ? 'warning' : 'success');
            } else {
                showNotification('Status updated successfully', 'success');
            }
            
            // Reload page after 1 second to refresh all data
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.message || 'Failed to update status', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification(error.message || 'An error occurred while updating status', 'error');
    });
}

function toggleUserApproval(url, itemId, linkElement) {
    console.log('toggleUserApproval called', { url, itemId });
    const csrfToken = getCSRFToken();
    if (!csrfToken) {
        console.error('CSRF token not found');
        showNotification('Security token not found. Please refresh the page.', 'error');
        return;
    }
    
    console.log('Sending approval request to:', url);
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || 'Server error');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update the link text and icon
            if (data.is_approved) {
                linkElement.innerHTML = '<i class="fas fa-check-circle me-2 text-success"></i>Unapprove';
            } else {
                linkElement.innerHTML = '<i class="fas fa-clock me-2 text-warning"></i>Approve';
            }
            
            // Update approval badge in the row
            const row = linkElement.closest('tr');
            const approvalBadge = row.querySelector('td:nth-child(5) .badge'); // Approval column
            if (approvalBadge && data.new_status) {
                approvalBadge.className = `badge ${data.new_status.class}`;
                approvalBadge.innerHTML = `<i class="fas ${data.new_status.icon} me-1"></i>${data.new_status.text}`;
            }
            
            showNotification(`User ${data.is_approved ? 'approved' : 'unapproved'} successfully`, 'success');
            
            // Reload page after 1 second to refresh all data
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.message || 'Failed to update approval status', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification(error.message || 'An error occurred while updating approval status', 'error');
    });
}

function resetUserPassword(url, itemId, linkElement) {
    const csrfToken = getCSRFToken();
    if (!csrfToken) {
        console.error('CSRF token not found');
        showNotification('Security token not found. Please refresh the page.', 'error');
        return;
    }
    
    console.log('Resetting password for user:', itemId);
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || 'Server error');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            const message = `Password reset successfully! New password: ${data.default_password || 'DefaultPass@12'}`;
            showNotification(message, 'success');
            
            // Optionally copy password to clipboard
            if (navigator.clipboard) {
                navigator.clipboard.writeText(data.default_password || 'DefaultPass@12').then(() => {
                    console.log('Password copied to clipboard');
                });
            }
        } else {
            showNotification(data.message || 'Failed to reset password', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification(error.message || 'An error occurred while resetting password', 'error');
    });
}

function deleteItem(url, itemId, rowElement) {
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the row with animation
            rowElement.style.transition = 'all 0.3s ease';
            rowElement.style.opacity = '0';
            rowElement.style.transform = 'translateX(-100%)';
            
            setTimeout(() => {
                rowElement.remove();
                
                // Update item count
                const countElement = document.getElementById('item-count');
                if (countElement) {
                    const currentCount = parseInt(countElement.textContent);
                    countElement.textContent = currentCount - 1;
                }
                
                // Check if table is empty
                const tbody = document.querySelector('#table-body');
                if (tbody && tbody.children.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="100%" class="text-center py-5">
                                <div class="text-600">
                                    <span class="fas fa-inbox fs-1 mb-3 d-block"></span>
                                    <h5 class="mb-2">No items found</h5>
                                    <p class="mb-0 text-muted">No data available at the moment.</p>
                                </div>
                            </td>
                        </tr>
                    `;
                }
            }, 300);
            
            showNotification('Item deleted successfully', 'success');
        } else {
            showNotification(data.message || 'Failed to delete item', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while deleting item', 'error');
    });
}

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification-toast');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification-toast alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; max-width: 400px;';
    
    const iconClass = type === 'success' ? 'fas fa-check-circle' : 
                     type === 'error' ? 'fas fa-exclamation-circle' : 
                     type === 'warning' ? 'fas fa-exclamation-triangle' : 'fas fa-info-circle';
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="${iconClass} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }
    }, 5000);
}














