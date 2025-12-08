/**
 * Common Actions JavaScript
 * 
 * Provides reusable functions for common UI actions like print, confirm dialogs, etc.
 * This file replaces inline event handlers (onclick, onchange) with proper event listeners.
 */

/**
 * Print the current page
 */
function printPage() {
    window.print();
}

/**
 * Show a confirmation dialog and execute callback if confirmed
 * 
 * @param {string} message - The confirmation message to display
 * @param {Function} callback - Function to execute if user confirms
 * @param {string} confirmText - Text for confirm button (default: "OK")
 * @param {string} cancelText - Text for cancel button (default: "Cancel")
 */
function confirmAction(message, callback, confirmText, cancelText) {
    confirmText = confirmText || 'OK';
    cancelText = cancelText || 'Cancel';
    
    if (window.confirm(message)) {
        if (typeof callback === 'function') {
            callback();
        }
        return true;
    }
    return false;
}

/**
 * Toggle visibility of an element by ID
 * 
 * @param {string} elementId - The ID of the element to toggle
 * @param {string} displayStyle - The display style to use when showing (default: 'block')
 */
function toggleElementVisibility(elementId, displayStyle) {
    displayStyle = displayStyle || 'block';
    const element = document.getElementById(elementId);
    
    if (element) {
        if (element.style.display === 'none' || !element.style.display) {
            element.style.display = displayStyle;
        } else {
            element.style.display = 'none';
        }
    }
}

/**
 * Show an element by ID
 * 
 * @param {string} elementId - The ID of the element to show
 * @param {string} displayStyle - The display style to use (default: 'block')
 */
function showElement(elementId, displayStyle) {
    displayStyle = displayStyle || 'block';
    const element = document.getElementById(elementId);
    
    if (element) {
        element.style.display = displayStyle;
    }
}

/**
 * Hide an element by ID
 * 
 * @param {string} elementId - The ID of the element to hide
 */
function hideElement(elementId) {
    const element = document.getElementById(elementId);
    
    if (element) {
        element.style.display = 'none';
    }
}

/**
 * Initialize print buttons - converts onclick="window.print()" to event listeners
 * 
 * @param {string} selector - CSS selector for print buttons (default: '.btn-print, [data-action="print"]')
 */
function initPrintButtons(selector) {
    selector = selector || '.btn-print, [data-action="print"]';
    const printButtons = document.querySelectorAll(selector);
    
    printButtons.forEach(function(button) {
        // Remove existing onclick handler if present
        button.removeAttribute('onclick');
        
        // Add event listener
        button.addEventListener('click', function(e) {
            e.preventDefault();
            printPage();
        });
    });
}

/**
 * Initialize confirmation buttons - converts onclick="return confirm(...)" to event listeners
 * 
 * @param {string} selector - CSS selector for confirmation buttons (default: '[data-confirm]')
 */
function initConfirmButtons(selector) {
    selector = selector || '[data-confirm]';
    const confirmButtons = document.querySelectorAll(selector);
    
    confirmButtons.forEach(function(button) {
        const message = button.getAttribute('data-confirm');
        if (!message) return;
        
        // Remove existing onclick handler if present
        button.removeAttribute('onclick');
        
        // Check if button is inside a form (for form submission)
        const form = button.closest('form');
        
        // Add event listener
        button.addEventListener('click', function(e) {
            if (!confirmAction(message)) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
            // If inside a form, let the form submit naturally
            // Otherwise, let the link navigate normally
        });
    });
}

/**
 * Initialize toggle buttons - converts onclick="document.getElementById(...).style.display='...'" to event listeners
 * 
 * @param {string} selector - CSS selector for toggle buttons (default: '[data-toggle]')
 */
function initToggleButtons(selector) {
    selector = selector || '[data-toggle]';
    const toggleButtons = document.querySelectorAll(selector);
    
    toggleButtons.forEach(function(button) {
        const targetId = button.getAttribute('data-toggle');
        const displayStyle = button.getAttribute('data-display') || 'block';
        
        if (!targetId) return;
        
        // Remove existing onclick handler if present
        button.removeAttribute('onclick');
        
        // Add event listener
        button.addEventListener('click', function(e) {
            e.preventDefault();
            toggleElementVisibility(targetId, displayStyle);
        });
    });
}

/**
 * Auto-initialize all common action buttons on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize print buttons
    initPrintButtons();
    
    // Initialize confirmation buttons
    initConfirmButtons();
    
    // Initialize toggle buttons
    initToggleButtons();
});

