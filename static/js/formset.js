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
        const currentRows = getFormsetRowCount(prefix, rowSelector);
        if (currentRows >= maxRows) {
            console.warn(`Maximum ${maxRows} rows allowed`);
            return false;
        }
    }
    
    // Get template row (support both template tag and regular elements)
    const templateElement = document.querySelector(templateSelector);
    if (!templateElement) {
        console.error(`Template element not found: ${templateSelector}`);
        return false;
    }
    
    // Handle template tag (use .content) or regular element
    let templateRow;
    if (templateElement.tagName === 'TEMPLATE') {
        // For template tag, get the first row from content
        const templateContent = templateElement.content;
        // Try to find row by class first (more reliable), then try tr, then firstElementChild
        templateRow = templateContent.querySelector('.formset-row') || 
                     templateContent.querySelector('.operation-row') ||
                     templateContent.querySelector('tr') || 
                     templateContent.firstElementChild;
        if (!templateRow) {
            console.error(`No row found in template: ${templateSelector}`);
            return false;
        }
    } else {
        templateRow = templateElement;
    }
    
    // Clone template row
    const newRow = templateRow.cloneNode(true);
    newRow.style.display = ''; // Make visible (template is usually hidden)
    
    // Ensure all child elements are visible (in case template had display:none)
    const allChildren = newRow.querySelectorAll('*');
    allChildren.forEach(child => {
      if (child.style && child.style.display === 'none') {
        child.style.display = '';
      }
    });
    
    console.log('Cloned row HTML length:', newRow.outerHTML.length);
    console.log('Cloned row has operation-form-fields:', !!newRow.querySelector('.operation-form-fields'));
    console.log('Cloned row children count:', newRow.children.length);
    
    // Get current form count
    const totalFormsInput = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
    if (!totalFormsInput) {
        console.error(`TOTAL_FORMS input not found for prefix: ${prefix}`);
        return false;
    }
    
    const currentFormCount = parseInt(totalFormsInput.value) || 0;
    const newFormIndex = currentFormCount;
    
    // Update all field names and IDs in the new row
    // CRITICAL: Django formsets always use __prefix__ pattern for empty forms
    // So we should always use prefix pattern when adding new rows
    const usePrefixPattern = true;  // Always use __prefix__ pattern for Django formsets
    
    // Log field names before update
    const inputsBefore = newRow.querySelectorAll('input, select, textarea');
    const namesBefore = Array.from(inputsBefore).map(inp => inp.name).filter(n => n && n.includes('__prefix__'));
    if (namesBefore.length > 0) {
        console.log(`Before updateRowFields: Found ${namesBefore.length} fields with __prefix__: ${namesBefore.slice(0, 3).join(', ')}...`);
    }
    
    updateRowFields(newRow, prefix, newFormIndex, usePrefixPattern);
    
    // Log field names after update
    const inputsAfter = newRow.querySelectorAll('input, select, textarea');
    const namesAfter = Array.from(inputsAfter).map(inp => inp.name).filter(n => n);
    const namesWithPrefix = namesAfter.filter(n => n.includes('__prefix__'));
    if (namesWithPrefix.length > 0) {
        console.error(`ERROR: After updateRowFields, still found ${namesWithPrefix.length} fields with __prefix__: ${namesWithPrefix.slice(0, 3).join(', ')}...`);
    } else {
        console.log(`After updateRowFields: All fields reindexed. Sample names: ${namesAfter.slice(0, 3).join(', ')}...`);
    }
    
    // Insert new row into formset container
    // For template tag or when tbodyId is specified, find the tbody or container
    let formsetContainer;
    if (templateElement.tagName === 'TEMPLATE' || options.tbodyId) {
        // Find the tbody that should contain the rows
        const tbodyId = options.tbodyId || `${prefix}-formset-body`;
        formsetContainer = document.getElementById(tbodyId);
        
        if (!formsetContainer) {
            // Try alternative selectors
            formsetContainer = document.querySelector(`#${prefix}-formset-body`) ||
                              document.querySelector(`tbody[id*="${prefix}"]`) ||
                              document.querySelector(`[data-formset-prefix="${prefix}"]`);
        }
        
        if (!formsetContainer) {
            // Fallback: find closest tbody or table
            const templateParent = templateElement.parentElement;
            formsetContainer = templateParent.querySelector('tbody') || 
                              templateParent.querySelector(`[id*="${prefix}"]`) ||
                              templateParent.querySelector(`[data-formset-prefix="${prefix}"]`) ||
                              templateParent;
        }
        
        if (!formsetContainer) {
            console.error(`Formset container not found for prefix: ${prefix}, tbodyId: ${tbodyId}`);
            return false;
        }
        
        console.log(`Adding row to container:`, formsetContainer);
        formsetContainer.appendChild(newRow);
    } else {
        // Regular element - insert before template
        formsetContainer = templateRow.closest('.formset-container') || templateRow.parentElement;
        if (!formsetContainer) {
            console.error(`Formset container not found for regular element`);
            return false;
        }
        formsetContainer.insertBefore(newRow, templateRow);
    }
    
    // Increment TOTAL_FORMS
    totalFormsInput.value = currentFormCount + 1;
    
    // Reindex all rows (to ensure sequential indices)
    reindexFormset(prefix, rowSelector, usePrefixPattern);
    
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
    const rowSelector = options.rowSelector || '.formset-row';
    const currentRows = getFormsetRowCount(prefix, rowSelector);
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
    // Note: usePrefixPattern is not available here, but reindexFormset defaults to false
    reindexFormset(prefix, rowSelector, false);
    
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
 * @param {boolean} usePrefixPattern - Whether to use __prefix__ pattern
 */
function reindexFormset(prefix, rowSelector = '.formset-row', usePrefixPattern = false) {
    // CRITICAL: For Django formsets, always use prefix pattern
    usePrefixPattern = true;
    
    const formsetContainer = document.querySelector(`[data-formset-prefix="${prefix}"]`) || 
                            document.querySelector(`.formset-container`) ||
                            document.querySelector(`#${prefix}-formset`) ||
                            document.querySelector(`.${prefix}-formset`);
    if (!formsetContainer) {
        console.warn(`Formset container not found for prefix: ${prefix}`);
        return;
    }
    
    const rows = formsetContainer.querySelectorAll(`${rowSelector}:not(.formset-template)`);
    let currentIndex = 0;
    
    console.log(`Reindexing formset ${prefix}: found ${rows.length} rows, usePrefixPattern=${usePrefixPattern}`);
    
    rows.forEach((row, index) => {
        // Skip deleted rows
        const deleteInput = row.querySelector(`input[name*="-DELETE"]`);
        if (deleteInput && deleteInput.checked) {
            console.log(`Skipping deleted row ${index}`);
            return; // Skip deleted rows
        }
        
        // Update all fields in this row
        console.log(`Reindexing row ${index} to index ${currentIndex} (usePrefixPattern=${usePrefixPattern})`);
        // Log field names before update
        const inputsBefore = row.querySelectorAll('input, select, textarea');
        const namesBefore = Array.from(inputsBefore).map(inp => inp.name).filter(n => n);
        if (namesBefore.length > 0) {
            console.log(`  Field names before: ${namesBefore.join(', ')}`);
        }
        updateRowFields(row, prefix, currentIndex, usePrefixPattern);
        // Log field names after update
        const inputsAfter = row.querySelectorAll('input, select, textarea');
        const namesAfter = Array.from(inputsAfter).map(inp => inp.name).filter(n => n);
        if (namesAfter.length > 0) {
            console.log(`  Field names after: ${namesAfter.join(', ')}`);
        }
        console.log(`Reindexed row ${index} to index ${currentIndex}`);
        
        // Update line number if exists
        const lineNumberElement = row.querySelector('.line-number');
        if (lineNumberElement) {
            lineNumberElement.textContent = currentIndex + 1;
        }
        
        // Update data-operation-index attribute on the row itself
        if (row.hasAttribute('data-operation-index')) {
            row.setAttribute('data-operation-index', currentIndex);
        }
        
        currentIndex++;
    });
    
    // Update TOTAL_FORMS
    updateFormsetTotal(prefix, rowSelector);
    console.log(`Reindexing complete: TOTAL_FORMS set to ${currentIndex}`);
}

/**
 * Update field names and IDs in a row.
 * 
 * @param {HTMLElement} row - Row element
 * @param {string} prefix - Formset prefix
 * @param {number} index - New index for this row
 * @param {boolean} usePrefixPattern - If true, use __prefix__ pattern instead of numeric pattern
 */
function updateRowFields(row, prefix, index, usePrefixPattern = false) {
    // Update all inputs, selects, textareas, buttons, and divs with data attributes
    const fields = row.querySelectorAll('input, select, textarea, label, button, div, tbody, span');
    
    let updatedCount = 0;
    fields.forEach(field => {
        if (usePrefixPattern) {
            // Use __prefix__ pattern (Django's default for empty forms)
            if (field.name && field.name.includes('__prefix__')) {
                const oldName = field.name;
                field.name = field.name.replace(/__prefix__/g, index);
                if (oldName !== field.name) {
                    updatedCount++;
                    console.log(`  Updated field name: ${oldName} -> ${field.name}`);
                }
            }
            if (field.id && field.id.includes('__prefix__')) {
                const oldId = field.id;
                field.id = field.id.replace(/__prefix__/g, index);
                if (oldId !== field.id) {
                    console.log(`  Updated field id: ${oldId} -> ${field.id}`);
                }
            }
            if (field.getAttribute('for') && field.getAttribute('for').includes('__prefix__')) {
                const oldFor = field.getAttribute('for');
                field.setAttribute('for', field.getAttribute('for').replace(/__prefix__/g, index));
                if (oldFor !== field.getAttribute('for')) {
                    console.log(`  Updated field for: ${oldFor} -> ${field.getAttribute('for')}`);
                }
            }
            // Update data attributes
            if (field.hasAttribute('data-field-index') && field.getAttribute('data-field-index') === '__prefix__') {
                field.setAttribute('data-field-index', index);
            }
            if (field.hasAttribute('data-permission-index') && field.getAttribute('data-permission-index') === '__prefix__') {
                field.setAttribute('data-permission-index', index);
            }
            if (field.hasAttribute('data-operation-index') && field.getAttribute('data-operation-index') === '__prefix__') {
                field.setAttribute('data-operation-index', index);
            }
        } else {
            // Use numeric pattern (prefix-N-)
            // Also handle __prefix__ pattern as fallback
            if (field.name) {
                // First try numeric pattern
                if (field.name.match(new RegExp(`${prefix}-\\d+-`))) {
                    field.name = field.name.replace(
                        new RegExp(`${prefix}-\\d+-`),
                        `${prefix}-${index}-`
                    );
                } else if (field.name.includes('__prefix__')) {
                    // Fallback to __prefix__ pattern
                    field.name = field.name.replace(/__prefix__/g, index);
                }
            }
            if (field.id) {
                // First try numeric pattern
                if (field.id.match(new RegExp(`${prefix}-\\d+-`))) {
                    field.id = field.id.replace(
                        new RegExp(`${prefix}-\\d+-`),
                        `${prefix}-${index}-`
                    );
                } else if (field.id.includes('__prefix__')) {
                    // Fallback to __prefix__ pattern
                    field.id = field.id.replace(/__prefix__/g, index);
                }
            }
            if (field.tagName === 'LABEL' && field.getAttribute('for')) {
                const forAttr = field.getAttribute('for');
                // First try numeric pattern
                if (forAttr.match(new RegExp(`${prefix}-\\d+-`))) {
                    field.setAttribute('for', forAttr.replace(
                        new RegExp(`${prefix}-\\d+-`),
                        `${prefix}-${index}-`
                    ));
                } else if (forAttr.includes('__prefix__')) {
                    // Fallback to __prefix__ pattern
                    field.setAttribute('for', forAttr.replace(/__prefix__/g, index));
                }
            }
        }
    });
}

/**
 * Get current row count for a formset.
 * 
 * @param {string} prefix - Formset prefix
 * @returns {number} - Number of visible rows
 */
function getFormsetRowCount(prefix, rowSelector = '.formset-row') {
    // First try to count actual DOM rows (more reliable)
    const formsetContainer = document.querySelector(`[data-formset-prefix="${prefix}"]`) || 
                            document.querySelector(`.formset-container`) ||
                            document.querySelector(`#${prefix}-formset`) ||
                            document.querySelector(`.${prefix}-formset`);
    
    if (formsetContainer) {
        const actualRows = formsetContainer.querySelectorAll(`${rowSelector}:not(.formset-template)`);
        const actualCount = Array.from(actualRows).filter(row => {
            // Exclude deleted rows
            const deleteInput = row.querySelector(`input[name*="-DELETE"]`);
            return !deleteInput || !deleteInput.checked;
        }).length;
        
        // Always use actual DOM count if container exists (even if 0)
        // This is more reliable than TOTAL_FORMS which might be incorrect
        return actualCount;
    }
    
    // Fallback to TOTAL_FORMS input only if container not found
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
    const usePrefixPattern = options.usePrefixPattern !== false;
    
    // Set formset prefix on container for easy selection
    const templateRow = document.querySelector(templateSelector);
    if (!templateRow) {
        console.error(`Template not found: ${templateSelector}`);
        return;
    }
    
    if (templateRow) {
        const container = templateRow.closest('.formset-container') || templateRow.parentElement;
        if (container) {
            container.setAttribute('data-formset-prefix', prefix);
            templateRow.classList.add('formset-template');
        }
    }
    
    // Add event listener for add button
    const addButton = document.querySelector(addButtonSelector);
    if (!addButton) {
        console.error(`Add button not found with selector: ${addButtonSelector}`);
        console.log('Available buttons:', document.querySelectorAll('.add-formset-row'));
        return;
    }
    
    console.log(`Formset initialized: ${prefix}, template: ${templateSelector}, button found:`, addButton);
    
    addButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log(`Add button clicked for formset: ${prefix}`);
        const result = addFormsetRow(prefix, templateSelector, options);
        if (!result) {
            console.error('Failed to add formset row');
        }
    });
    
    // Add event listeners for remove buttons (existing and future)
    document.addEventListener('click', function(e) {
        if (e.target.matches(removeButtonSelector)) {
            e.preventDefault();
            removeFormsetRow(e.target, prefix, { minRows, rowSelector });
        }
    });
    
    // Ensure minimum rows
    const currentRows = getFormsetRowCount(prefix, rowSelector);
    console.log(`Formset ${prefix}: currentRows=${currentRows}, minRows=${minRows}`);
    if (currentRows < minRows) {
        const rowsToAdd = minRows - currentRows;
        console.log(`Formset ${prefix}: Adding ${rowsToAdd} row(s) to meet minimum`);
        for (let i = 0; i < rowsToAdd; i++) {
            addFormsetRow(prefix, templateSelector, options);
        }
    } else {
        console.log(`Formset ${prefix}: Already has ${currentRows} row(s), no need to add more`);
    }
    
    // Initial reindex
    // CRITICAL: Always use prefix pattern for Django formsets (they use __prefix__ in empty forms)
    reindexFormset(prefix, rowSelector, true);
}



