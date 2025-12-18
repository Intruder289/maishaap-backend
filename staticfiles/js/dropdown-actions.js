// Dropdown Actions JavaScript
// This file handles all dropdown action functionality across the application

document.addEventListener('DOMContentLoaded', function() {
    // Handle dropdown actions
    document.addEventListener('click', function(e) {
        // Handle toggle status action
        if (e.target.closest('.toggle-status-action')) {
            e.preventDefault();
            const link = e.target.closest('.toggle-status-action');
            const url = link.dataset.url;
            const itemId = link.dataset.itemId;
            
            if (confirm('Are you sure you want to change the status of this item?')) {
                toggleItemStatus(url, itemId, link);
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
            const statusBadge = row.querySelector('.status-badge');
            if (statusBadge && data.new_status) {
                statusBadge.className = `badge ${data.new_status.class}`;
                statusBadge.textContent = data.new_status.text;
            }
            
            showNotification('Status updated successfully', 'success');
        } else {
            showNotification(data.message || 'Failed to update status', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while updating status', 'error');
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





