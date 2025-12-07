/**
 * Formset management utilities for Django formsets.
 * 
 * This file provides common functions for managing dynamic formsets:
 * - Adding new rows
 * - Removing rows
 * - Updating form indices
 * - Managing TOTAL_FORMS counter
 */

/**
 * Add a new row to a formset.
 * 
 * @param {string} prefix - Formset prefix (e.g., 'formset')
 * @param {string} templateSelector - CSS selector for template row (e.g., '#formset-template-row')
 * @param {Object} options - Configuration options
 * @param {number} options.minRows - Minimum number of rows (default: 1)
 * @param {number} options.maxRows - Maximum number of rows (null = unlimited, default: null)
 * @param {string} options.rowSelector - CSS selector for row elements (default: '.formset-row')
 * @returns {boolean} - True if row was added, false otherwise
 */
function addFormsetRow(prefix, templateSelector, options = {}) {
    const minRows = options.minRows || 1;
    const maxRows = options.maxRows || null;
    const rowSelector = options.rowSelector || '.formset-row';
    
    // Check max rows limit
    if (maxRows !== null) {
        const currentRows = getFormsetRowCount(prefix);
        if (currentRows >= maxRows) {
            console.warn(`Maximum ${maxRows} rows allowed`);
            return false;
        }
    }
    
    // Get template row
    const templateRow = document.querySelector(templateSelector);
    if (!templateRow) {
        console.error(`Template row not found: ${templateSelector}`);
        return false;
    }
    
    // Clone template row
    const newRow = templateRow.cloneNode(true);
    newRow.style.display = ''; // Make visible (template is usually hidden)
    
    // Get current form count
    const totalFormsInput = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
    if (!totalFormsInput) {
        console.error(`TOTAL_FORMS input not found for prefix: ${prefix}`);
        return false;
    }
    
    const currentFormCount = parseInt(totalFormsInput.value) || 0;
    const newFormIndex = currentFormCount;
    
    // Update all field names and IDs in the new row
    updateRowFields(newRow, prefix, newFormIndex);
    
    // Insert new row before template row (or append to formset container)
    const formsetContainer = templateRow.closest('.formset-container') || templateRow.parentElement;
    formsetContainer.insertBefore(newRow, templateRow);
    
    // Increment TOTAL_FORMS
    totalFormsInput.value = currentFormCount + 1;
    
    // Reindex all rows (to ensure sequential indices)
    reindexFormset(prefix, rowSelector);
    
    // Trigger custom event
    const event = new CustomEvent('formset:row-added', {
        detail: { prefix, index: newFormIndex, row: newRow }
    });
    document.dispatchEvent(event);
    
    return true;
}

/**
 * Remove a row from formset.
 * 
 * @param {HTMLElement} button - Remove button element
 * @param {string} prefix - Formset prefix
 * @param {Object} options - Configuration options
 * @param {number} options.minRows - Minimum number of rows (default: 1)
 * @param {string} options.rowSelector - CSS selector for row elements (default: '.formset-row')
 * @returns {boolean} - True if row was removed, false otherwise
 */
function removeFormsetRow(button, prefix, options = {}) {
    const minRows = options.minRows || 1;
    const rowSelector = options.rowSelector || '.formset-row';
    
    // Get row to remove
    const row = button.closest('tr') || button.closest(rowSelector) || button.parentElement;
    if (!row) {
        console.error('Row not found');
        return false;
    }
    
    // Check minimum rows requirement
    const currentRows = getFormsetRowCount(prefix);
    if (currentRows <= minRows) {
        console.warn(`Minimum ${minRows} rows required`);
        return false;
    }
    
    // Mark as deleted (if DELETE field exists)
    const deleteInput = row.querySelector(`input[name*="-DELETE"]`);
    if (deleteInput) {
        deleteInput.checked = true;
        row.style.display = 'none'; // Hide instead of removing
    } else {
        // No DELETE field - remove completely
        row.remove();
    }
    
    // Update TOTAL_FORMS
    updateFormsetTotal(prefix, rowSelector);
    
    // Reindex all rows
    reindexFormset(prefix, rowSelector);
    
    // Trigger custom event
    const event = new CustomEvent('formset:row-removed', {
        detail: { prefix, row }
    });
    document.dispatchEvent(event);
    
    return true;
}

/**
 * Update TOTAL_FORMS hidden input.
 * 
 * @param {string} prefix - Formset prefix
 * @param {string} rowSelector - CSS selector for row elements (default: '.formset-row')
 */
function updateFormsetTotal(prefix, rowSelector = '.formset-row') {
    const totalFormsInput = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
    if (!totalFormsInput) {
        console.error(`TOTAL_FORMS input not found for prefix: ${prefix}`);
        return;
    }
    
    // Count visible rows (excluding template and deleted rows)
    const formsetContainer = document.querySelector(`[data-formset-prefix="${prefix}"]`) || 
                            document.querySelector(`.formset-container`);
    if (!formsetContainer) {
        // Fallback: count by field name pattern
        const visibleRows = document.querySelectorAll(`[name*="${prefix}-"][name*="-id"]`);
        const visibleCount = Array.from(visibleRows).filter(input => {
            const row = input.closest('tr') || input.closest(rowSelector);
            return row && row.style.display !== 'none' && !row.classList.contains('formset-template');
        }).length;
        totalFormsInput.value = visibleCount;
        return;
    }
    
    const visibleRows = formsetContainer.querySelectorAll(`${rowSelector}:not(.formset-template)`);
    const visibleCount = Array.from(visibleRows).filter(row => {
        const deleteInput = row.querySelector(`input[name*="-DELETE"]`);
        return !deleteInput || !deleteInput.checked;
    }).length;
    
    totalFormsInput.value = visibleCount;
}

/**
 * Reindex all formset rows.
 * 
 * @param {string} prefix - Formset prefix
 * @param {string} rowSelector - CSS selector for row elements (default: '.formset-row')
 */
function reindexFormset(prefix, rowSelector = '.formset-row') {
    const formsetContainer = document.querySelector(`[data-formset-prefix="${prefix}"]`) || 
                            document.querySelector(`.formset-container`);
    if (!formsetContainer) {
        console.warn(`Formset container not found for prefix: ${prefix}`);
        return;
    }
    
    const rows = formsetContainer.querySelectorAll(`${rowSelector}:not(.formset-template)`);
    let currentIndex = 0;
    
    rows.forEach((row, index) => {
        // Skip deleted rows
        const deleteInput = row.querySelector(`input[name*="-DELETE"]`);
        if (deleteInput && deleteInput.checked) {
            return; // Skip deleted rows
        }
        
        // Update all fields in this row
        updateRowFields(row, prefix, currentIndex);
        
        // Update line number if exists
        const lineNumberElement = row.querySelector('.line-number');
        if (lineNumberElement) {
            lineNumberElement.textContent = currentIndex + 1;
        }
        
        currentIndex++;
    });
    
    // Update TOTAL_FORMS
    updateFormsetTotal(prefix, rowSelector);
}

/**
 * Update field names and IDs in a row.
 * 
 * @param {HTMLElement} row - Row element
 * @param {string} prefix - Formset prefix
 * @param {number} index - New index for this row
 */
function updateRowFields(row, prefix, index) {
    // Update all inputs, selects, textareas
    const fields = row.querySelectorAll('input, select, textarea, label');
    
    fields.forEach(field => {
        // Update name attribute
        if (field.name) {
            field.name = field.name.replace(
                new RegExp(`${prefix}-\\d+-`),
                `${prefix}-${index}-`
            );
        }
        
        // Update id attribute
        if (field.id) {
            field.id = field.id.replace(
                new RegExp(`${prefix}-\\d+-`),
                `${prefix}-${index}-`
            );
        }
        
        // Update label 'for' attribute
        if (field.tagName === 'LABEL' && field.getAttribute('for')) {
            const forAttr = field.getAttribute('for');
            field.setAttribute('for', forAttr.replace(
                new RegExp(`${prefix}-\\d+-`),
                `${prefix}-${index}-`
            ));
        }
    });
}

/**
 * Get current row count for a formset.
 * 
 * @param {string} prefix - Formset prefix
 * @returns {number} - Number of visible rows
 */
function getFormsetRowCount(prefix) {
    const totalFormsInput = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
    if (totalFormsInput) {
        return parseInt(totalFormsInput.value) || 0;
    }
    return 0;
}

/**
 * Initialize formset with event handlers.
 * 
 * @param {string} prefix - Formset prefix
 * @param {string} templateSelector - CSS selector for template row
 * @param {Object} options - Configuration options
 * @param {number} options.minRows - Minimum number of rows (default: 1)
 * @param {number} options.maxRows - Maximum number of rows (null = unlimited, default: null)
 * @param {string} options.addButtonSelector - Selector for add button (default: `.add-formset-row`)
 * @param {string} options.removeButtonSelector - Selector for remove buttons (default: `.remove-formset-row`)
 * @param {string} options.rowSelector - CSS selector for row elements (default: '.formset-row')
 */
function initFormset(prefix, templateSelector, options = {}) {
    const minRows = options.minRows || 1;
    const maxRows = options.maxRows || null;
    const addButtonSelector = options.addButtonSelector || `.add-formset-row[data-prefix="${prefix}"]`;
    const removeButtonSelector = options.removeButtonSelector || `.remove-formset-row[data-prefix="${prefix}"]`;
    const rowSelector = options.rowSelector || '.formset-row';
    
    // Set formset prefix on container for easy selection
    const templateRow = document.querySelector(templateSelector);
    if (templateRow) {
        const container = templateRow.closest('.formset-container') || templateRow.parentElement;
        if (container) {
            container.setAttribute('data-formset-prefix', prefix);
            templateRow.classList.add('formset-template');
        }
    }
    
    // Add event listener for add button
    const addButton = document.querySelector(addButtonSelector);
    if (addButton) {
        addButton.addEventListener('click', function(e) {
            e.preventDefault();
            addFormsetRow(prefix, templateSelector, { minRows, maxRows, rowSelector });
        });
    }
    
    // Add event listeners for remove buttons (existing and future)
    document.addEventListener('click', function(e) {
        if (e.target.matches(removeButtonSelector)) {
            e.preventDefault();
            removeFormsetRow(e.target, prefix, { minRows, rowSelector });
        }
    });
    
    // Ensure minimum rows
    const currentRows = getFormsetRowCount(prefix);
    if (currentRows < minRows) {
        const rowsToAdd = minRows - currentRows;
        for (let i = 0; i < rowsToAdd; i++) {
            addFormsetRow(prefix, templateSelector, { minRows, maxRows, rowSelector });
        }
    }
    
    // Initial reindex
    reindexFormset(prefix, rowSelector);
}



