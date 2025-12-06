/**
 * Approval and Reject action utilities for submitting approval/reject forms.
 * 
 * This file provides generic functions for handling approval and reject actions
 * that create and submit forms dynamically.
 */

/**
 * Submit an approval or reject action via POST form.
 * 
 * @param {string|number} objectId - ID of the object to approve/reject
 * @param {string} actionUrl - URL to submit the form to
 * @param {string} confirmMessage - Confirmation message to show before submitting
 * @param {Object} options - Configuration options
 * @param {Function} options.onSuccess - Callback function called after successful submission
 * @param {Function} options.onError - Callback function called if submission fails
 * @param {boolean} options.skipConfirm - Skip confirmation dialog (default: false)
 */
function submitApprovalAction(objectId, actionUrl, confirmMessage, options = {}) {
    const config = {
        onSuccess: options.onSuccess || null,
        onError: options.onError || null,
        skipConfirm: options.skipConfirm || false
    };
    
    // Show confirmation dialog unless skipped
    if (!config.skipConfirm && confirmMessage) {
        if (!confirm(confirmMessage)) {
            return;
        }
    }
    
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfToken) {
        console.error('CSRF token not found');
        if (config.onError) {
            config.onError(new Error('CSRF token not found'));
        }
        return;
    }
    
    // Create form
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = actionUrl.replace('0', objectId.toString());
    
    // Add CSRF token
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken.value;
    form.appendChild(csrfInput);
    
    // Append form to body and submit
    document.body.appendChild(form);
    
    try {
        form.submit();
        if (config.onSuccess) {
            config.onSuccess();
        }
    } catch (error) {
        console.error('Error submitting approval action:', error);
        if (config.onError) {
            config.onError(error);
        }
        document.body.removeChild(form);
    }
}

/**
 * Approve an object.
 * 
 * @param {string|number} objectId - ID of the object to approve
 * @param {string} approveUrl - URL template for approve action (should contain '0' as placeholder)
 * @param {string} confirmMessage - Confirmation message (default: generic approve message)
 */
function approveObject(objectId, approveUrl, confirmMessage = null) {
    const defaultMessage = 'Are you sure you want to approve this item?';
    submitApprovalAction(
        objectId,
        approveUrl,
        confirmMessage || defaultMessage
    );
}

/**
 * Reject an object.
 * 
 * @param {string|number} objectId - ID of the object to reject
 * @param {string} rejectUrl - URL template for reject action (should contain '0' as placeholder)
 * @param {string} confirmMessage - Confirmation message (default: generic reject message)
 */
function rejectObject(objectId, rejectUrl, confirmMessage = null) {
    const defaultMessage = 'Are you sure you want to reject this item?';
    submitApprovalAction(
        objectId,
        rejectUrl,
        confirmMessage || defaultMessage
    );
}

