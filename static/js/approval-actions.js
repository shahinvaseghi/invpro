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
 * @param {Object} options - Configuration options
 * @param {boolean} options.useFetch - Use fetch API instead of form submission (default: false)
 */
function approveObject(objectId, approveUrl, confirmMessage = null, options = {}) {
    const config = {
        useFetch: options.useFetch || false
    };
    
    const defaultMessage = 'Are you sure you want to approve this item?';
    
    // Use fetch API if requested
    if (config.useFetch) {
        submitApprovalActionFetch(
            objectId,
            approveUrl,
            confirmMessage || defaultMessage
        );
        return;
    }
    
    // Use form submission (default)
    submitApprovalAction(
        objectId,
        approveUrl,
        confirmMessage || defaultMessage
    );
}

/**
 * Submit an approval or reject action via fetch API (AJAX).
 * 
 * @param {string|number} objectId - ID of the object to approve/reject
 * @param {string} actionUrl - URL to submit the request to
 * @param {string} confirmMessage - Confirmation message to show before submitting
 * @param {Object} options - Configuration options
 * @param {Function} options.onSuccess - Callback function called after successful submission
 * @param {Function} options.onError - Callback function called if submission fails
 * @param {boolean} options.skipConfirm - Skip confirmation dialog (default: false)
 * @param {Object} options.extraData - Extra data to send with the request
 */
function submitApprovalActionFetch(objectId, actionUrl, confirmMessage, options = {}) {
    const config = {
        onSuccess: options.onSuccess || null,
        onError: options.onError || null,
        skipConfirm: options.skipConfirm || false,
        extraData: options.extraData || {}
    };
    
    // Show confirmation dialog unless skipped
    if (!config.skipConfirm && confirmMessage) {
        if (!confirm(confirmMessage)) {
            return;
        }
    }
    
    // Get CSRF token
    function getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            return csrfToken.value;
        }
        // Try to get from cookies (Django sets csrftoken cookie)
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return null;
    }
    
    const csrfToken = getCSRFToken();
    if (!csrfToken) {
        console.error('CSRF token not found');
        if (config.onError) {
            config.onError(new Error('CSRF token not found'));
        }
        return;
    }
    
    const url = actionUrl.replace('0', objectId.toString());
    
    // Prepare request body
    const body = {
        ...config.extraData
    };
    
    // Make fetch request
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
        body: Object.keys(body).length > 0 ? JSON.stringify(body) : undefined
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (config.onSuccess) {
                config.onSuccess(data);
            } else {
                // Default: reload page
                window.location.reload();
            }
        } else {
            const error = new Error(data.error || 'An error occurred');
            if (config.onError) {
                config.onError(error);
            } else {
                alert(data.error || 'An error occurred');
            }
        }
    })
    .catch(error => {
        console.error('Error submitting approval action:', error);
        if (config.onError) {
            config.onError(error);
        } else {
            alert('An error occurred while processing the request.');
        }
    });
}

/**
 * Reject an object.
 * 
 * @param {string|number} objectId - ID of the object to reject
 * @param {string} rejectUrl - URL template for reject action (should contain '0' as placeholder)
 * @param {string} confirmMessage - Confirmation message (default: generic reject message)
 * @param {Object} options - Configuration options
 * @param {boolean} options.requireNotes - Require notes/reason for rejection (default: false)
 * @param {string} options.notesPrompt - Prompt message for notes (default: 'Please provide a reason for rejection:')
 * @param {string} options.notesFieldName - Field name for notes in form (default: 'qc_notes')
 * @param {boolean} options.useFetch - Use fetch API instead of form submission (default: false)
 */
function rejectObject(objectId, rejectUrl, confirmMessage = null, options = {}) {
    const config = {
        requireNotes: options.requireNotes || false,
        notesPrompt: options.notesPrompt || 'Please provide a reason for rejection:',
        notesFieldName: options.notesFieldName || 'qc_notes',
        useFetch: options.useFetch || false
    };
    
    const defaultMessage = 'Are you sure you want to reject this item?';
    
    // If notes are required, get them first
    let notes = null;
    if (config.requireNotes) {
        notes = prompt(config.notesPrompt);
        if (notes === null) {
            return; // User cancelled
        }
        if (notes.trim() === '') {
            alert('Notes are required for rejection.');
            return;
        }
    }
    
    // Show confirmation dialog unless notes prompt was cancelled
    if (!confirmMessage || !confirm(confirmMessage || defaultMessage)) {
        return;
    }
    
    // Use fetch API if requested
    if (config.useFetch) {
        const extraData = {};
        if (notes) {
            extraData[config.notesFieldName] = notes;
        }
        submitApprovalActionFetch(
            objectId,
            rejectUrl,
            null, // Already confirmed
            {
                skipConfirm: true,
                extraData: extraData
            }
        );
        return;
    }
    
    // Use form submission (default)
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfToken) {
        console.error('CSRF token not found');
        return;
    }
    
    // Create form
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = rejectUrl.replace('0', objectId.toString());
    
    // Add CSRF token
    const csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken.value;
    form.appendChild(csrfInput);
    
    // Add notes if provided
    if (notes) {
        const notesInput = document.createElement('input');
        notesInput.type = 'hidden';
        notesInput.name = config.notesFieldName;
        notesInput.value = notes;
        form.appendChild(notesInput);
    }
    
    // Append form to body and submit
    document.body.appendChild(form);
    form.submit();
}

