/**
 * Warehouse Request Form JavaScript
 * 
 * Handles:
 * - Jalali date picker initialization
 * - Formset management (remove extra rows, layout)
 * - Item filters initialization
 */

(function() {
  'use strict';

  /**
   * Initialize Jalali DatePicker for date inputs
   */
  function initJalaliDatePicker() {
    const dateInputs = document.querySelectorAll('.jalali-date-input, input[data-jalali="true"]');
    dateInputs.forEach(function(input) {
      // Ensure data attributes are set
      if (!input.hasAttribute('data-jdp')) {
        input.setAttribute('data-jdp', '');
      }
      if (!input.hasAttribute('data-jdp-only-date')) {
        input.setAttribute('data-jdp-only-date', '');
      }
    });
    
    // Start watching for Jalali DatePicker initialization
    if (typeof jalaliDatepicker !== 'undefined') {
      jalaliDatepicker.startWatch({
        date: true,
        time: false,
        separatorChars: {
          date: '/',
          between: ' ',
          time: ':'
        },
        persianDigits: false,
        autoShow: true,
        autoHide: true,
        hideAfterChange: true,
        showTodayBtn: true,
        showEmptyBtn: true,
        showCloseBtn: true,
        useDropDownYears: true,
        zIndex: 1000
      });
    } else {
      console.error('Jalali DatePicker library not loaded!');
    }
  }

  /**
   * Remove extra empty rows from formset
   * Keeps only the first row if multiple empty rows exist
   * IMPORTANT: Never remove all rows - always keep at least one row
   */
  function removeExtraRows(formsetContainer, totalFormsInput) {
    if (!formsetContainer || !totalFormsInput) {
      return;
    }

    // Get all rows (excluding template which doesn't exist yet)
    const existingRows = Array.from(formsetContainer.querySelectorAll('.line-row:not(.formset-template)'));
    
    console.log('Initial rows count:', existingRows.length);
    console.log('TOTAL_FORMS value:', totalFormsInput.value);
    
    // IMPORTANT: Always keep at least 1 row (minimum required by formset)
    // Only remove extra rows if we have more than 1
    if (existingRows.length > 1) {
      // Keep only the first row, remove all others
      // Remove from end to avoid index shifting issues
      for (let i = existingRows.length - 1; i > 0; i--) {
        console.log('Removing extra row:', i);
        const rowToRemove = existingRows[i];
        // CRITICAL: Use isRowEmpty function to properly check if row is empty
        // This checks both item AND quantity, not just item
        const isEmpty = isRowEmpty(rowToRemove);
        const isDeleted = rowToRemove.classList.contains('deleted');
        
        // Only remove if row is TRULY empty and not deleted
        // IMPORTANT: Never remove rows that have any data (item or quantity)
        if (isEmpty && !isDeleted && rowToRemove && rowToRemove.parentNode) {
          console.log(`Removing empty row ${i} (no item or quantity)`);
          rowToRemove.remove();
        } else {
          console.log(`Keeping row ${i} (has data or is deleted)`);
        }
      }
      // Update TOTAL_FORMS
      const remainingRows = formsetContainer.querySelectorAll('.line-row:not(.formset-template)');
      const remainingCount = remainingRows.length;
      // Ensure at least 1 row exists
      if (remainingCount === 0) {
        console.warn('No rows remaining, this should not happen!');
        totalFormsInput.value = '1';
      } else {
        totalFormsInput.value = remainingCount.toString();
      }
      console.log('Updated TOTAL_FORMS to', totalFormsInput.value);
      
      // Force reflow to ensure DOM is updated
      formsetContainer.offsetHeight;
    } else if (existingRows.length === 0) {
      // If no rows exist, this is an error - formset should have at least 1 row
      console.error('No rows found in formset! Formset should have at least 1 empty row.');
      totalFormsInput.value = '1';
    }
  }

  /**
   * Apply grid layout to formset table
   */
  function applyFormsetLayout(formsetContainer) {
    if (!formsetContainer) {
      return;
    }

    // Try to use shared function first
    if (typeof initFormsetTableLayout === 'function') {
      initFormsetTableLayout(formsetContainer, {
        columnsWithDelete: '50px 3fr 1.5fr 1.5fr 2fr 2fr 80px',
        columnsWithoutDelete: '50px 3fr 1.5fr 1.5fr 2fr 2fr',
      });
    } else {
      // Fallback: apply CSS directly
      const header = formsetContainer.querySelector('.lines-table-header');
      const rows = formsetContainer.querySelectorAll('.line-row:not(.formset-template)');
      const canDelete = formsetContainer.getAttribute('data-can-delete') === 'true';
      const gridColumns = canDelete ? '50px 3fr 1.5fr 1.5fr 2fr 2fr 80px' : '50px 3fr 1.5fr 1.5fr 2fr 2fr';
      
      if (header) {
        header.style.gridTemplateColumns = gridColumns;
        header.style.display = 'grid';
      }
      rows.forEach(function(row) {
        row.style.gridTemplateColumns = gridColumns;
        row.style.display = 'grid';
      });
    }
  }

  /**
   * Initialize line forms (re-index and apply filters)
   */
  function initializeLineForms(formsetContainer, filterOptions) {
    if (!formsetContainer) {
      return;
    }

    const rows = formsetContainer.querySelectorAll('.line-row:not(.formset-template)');
    rows.forEach(function(lineRow, index) {
      const lineNumber = lineRow.querySelector('.line-number');
      if (lineNumber) {
        lineNumber.textContent = index + 1;
      }
      
      // Use shared item-filters.js function if available
      if (typeof initializeItemFiltersForRow === 'function') {
        initializeItemFiltersForRow(lineRow, filterOptions);
      } else {
        console.warn('initializeItemFiltersForRow function not found. Make sure item-filters.js is loaded.');
      }
    });
  }

  /**
   * Initialize formset with formset.js
   */
  function initFormsetManagement(formsetContainer, addLineBtn, totalFormsInput, filterOptions) {
    if (!addLineBtn || !formsetContainer || !totalFormsInput) {
      return;
    }

    // Clone first row as template
    const firstRow = formsetContainer.querySelector('.line-row:not(.formset-template)');
    if (!firstRow) {
      console.error('No existing row found to use as template');
      // Try to wait a bit and check again (in case DOM is not fully ready)
      setTimeout(function() {
        const retryRow = formsetContainer.querySelector('.line-row:not(.formset-template)');
        if (retryRow) {
          console.log('Found row on retry, initializing formset...');
          initFormsetManagement(formsetContainer, addLineBtn, totalFormsInput, filterOptions);
        } else {
          console.error('Still no row found after retry. Formset may be empty.');
        }
      }, 100);
      return;
    }

    const templateRow = firstRow.cloneNode(true);
    templateRow.id = 'lines-formset-template';
    templateRow.style.display = 'none';
    templateRow.classList.add('formset-template');
    formsetContainer.appendChild(templateRow);
    
    // Initialize formset
    if (typeof initFormset === 'function') {
      initFormset('lines', '#lines-formset-template', {
        minRows: 1,
        maxRows: null,
        addButtonSelector: '#add-line-btn',
        removeButtonSelector: '.line-delete input[type="checkbox"]'
      });
    }
    
    // After adding row, initialize filters and update layout
    document.addEventListener('formset:row-added', function(e) {
      if (e.detail.prefix === 'lines') {
        setTimeout(function() {
          const newRow = formsetContainer.querySelector('.line-row:not(.formset-template)');
          if (newRow) {
            if (typeof initializeItemFiltersForRow === 'function') {
              initializeItemFiltersForRow(newRow, filterOptions);
            }
            initializeLineForms(formsetContainer, filterOptions);
            if (typeof updateFormsetTableLayout === 'function') {
              updateFormsetTableLayout(formsetContainer, {
                columnsWithDelete: '50px 3fr 1.5fr 1.5fr 2fr 2fr 80px',
                columnsWithoutDelete: '50px 3fr 1.5fr 1.5fr 2fr 2fr',
              });
            } else {
              applyFormsetLayout(formsetContainer);
            }
          }
        }, 50);
      }
    });
  }

  /**
   * Handle delete checkboxes
   */
  function initDeleteCheckboxes(formsetContainer, filterOptions) {
    if (!formsetContainer) {
      return;
    }

    // Use event delegation to handle dynamically added checkboxes
    formsetContainer.addEventListener('change', function(e) {
      if (e.target.type === 'checkbox' && e.target.name && e.target.name.includes('-DELETE')) {
        const lineRow = e.target.closest('.line-row');
        if (lineRow && !lineRow.classList.contains('formset-template')) {
          if (e.target.checked) {
            lineRow.classList.add('deleted');
            // Disable form fields in deleted row
            const inputs = lineRow.querySelectorAll('input, select, textarea');
            inputs.forEach(function(input) {
              if (input.name && !input.name.includes('-DELETE')) {
                input.disabled = true;
              }
            });
          } else {
            lineRow.classList.remove('deleted');
            // Re-enable form fields
            const inputs = lineRow.querySelectorAll('input, select, textarea');
            inputs.forEach(function(input) {
              if (input.name && !input.name.includes('-DELETE')) {
                input.disabled = false;
              }
            });
          }
          // Update row numbers after delete toggle
          initializeLineForms(formsetContainer, filterOptions || {});
        }
      }
    });
    
    // Also handle initial state of checkboxes
    const deleteCheckboxes = formsetContainer.querySelectorAll('input[type="checkbox"][name*="-DELETE"]');
    deleteCheckboxes.forEach(function(checkbox) {
      const lineRow = checkbox.closest('.line-row');
      if (lineRow && !lineRow.classList.contains('formset-template')) {
        if (checkbox.checked) {
          lineRow.classList.add('deleted');
          const inputs = lineRow.querySelectorAll('input, select, textarea');
          inputs.forEach(function(input) {
            if (input.name && !input.name.includes('-DELETE')) {
              input.disabled = true;
            }
          });
        }
      }
    });
  }

  /**
   * Check if a row has any data filled in
   * Note: We only check item and quantity here. Warehouse validation is done in backend.
   * This prevents rows from being removed prematurely when user is still filling the form.
   */
  function isRowEmpty(row) {
    if (!row) return true;
    
    const itemSelect = row.querySelector('select[name*="-item"]');
    const quantityInput = row.querySelector('input[name*="-quantity_requested"]');
    
    const hasItem = itemSelect && itemSelect.value && itemSelect.value !== '';
    const hasQuantity = quantityInput && quantityInput.value && parseFloat(quantityInput.value) > 0;
    
    // Row is considered empty if it doesn't have at least item and quantity
    // Warehouse validation will be done in backend
    return !hasItem || !hasQuantity;
  }

  /**
   * Extract form index from a name or id attribute
   */
  function getFormIndexFromName(name) {
    const match = name.match(/lines-(\d+)-/);
    return match ? parseInt(match[1]) : null;
  }

  /**
   * Update form index in a name or id attribute
   */
  function updateFormIndexInName(name, newIndex) {
    return name.replace(/lines-\d+-/, 'lines-' + newIndex + '-');
  }

  /**
   * Remove empty rows and update formset indices
   * IMPORTANT: Only remove rows that are TRULY empty (no item, no quantity)
   * Do NOT remove rows that have data, even if some fields are missing
   */
  function removeEmptyRows(formsetContainer, totalFormsInput) {
    if (!formsetContainer || !totalFormsInput) {
      return 0;
    }

    const rows = Array.from(formsetContainer.querySelectorAll('.line-row:not(.formset-template)'));
    const canDelete = formsetContainer.getAttribute('data-can-delete') === 'true';
    
    let validRows = [];
    let removedCount = 0;
    
    // First pass: identify valid and empty rows
    rows.forEach(function(row) {
      // Check if row is marked for deletion
      const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
      const isDeleted = deleteCheckbox && deleteCheckbox.checked;
      
      // Check if row is empty (only checks item and quantity, not warehouse)
      const isEmpty = isRowEmpty(row);
      
      if (isDeleted) {
        // Row is marked for deletion - keep it but mark as deleted
        const hiddenId = row.querySelector('input[type="hidden"][name*="-id"]');
        const hasId = hiddenId && hiddenId.value && hiddenId.value !== '';
        
        if (hasId && canDelete) {
          // Mark existing row for deletion
          if (deleteCheckbox) {
            deleteCheckbox.checked = true;
            row.classList.add('deleted');
            // Disable form fields
            const inputs = row.querySelectorAll('input, select, textarea');
            inputs.forEach(function(input) {
              if (input.name && !input.name.includes('-DELETE') && !input.name.includes('-id')) {
                input.disabled = true;
              }
            });
          }
          validRows.push(row);
        } else {
          // New row marked for deletion - remove it
          row.remove();
          removedCount++;
        }
      } else if (isEmpty) {
        // Row is empty - only remove if it's a new row (no ID)
        const hiddenId = row.querySelector('input[type="hidden"][name*="-id"]');
        const hasId = hiddenId && hiddenId.value && hiddenId.value !== '';
        
        if (hasId && canDelete) {
          // Existing row that became empty - mark for deletion
          if (deleteCheckbox) {
            deleteCheckbox.checked = true;
            row.classList.add('deleted');
            const inputs = row.querySelectorAll('input, select, textarea');
            inputs.forEach(function(input) {
              if (input.name && !input.name.includes('-DELETE') && !input.name.includes('-id')) {
                input.disabled = true;
              }
            });
          }
          validRows.push(row);
        } else {
          // New empty row - remove it ONLY if it's truly empty
          // Double-check using isRowEmpty to be safe
          const reallyEmpty = isRowEmpty(row);
          if (reallyEmpty) {
            console.log(`Removing new empty row (no item or quantity)`);
            row.remove();
            removedCount++;
          } else {
            // Row has data, keep it
            console.log(`Keeping row that appeared empty but has data`);
            validRows.push(row);
          }
        }
      } else {
        // Row has data - always keep it
        // IMPORTANT: Ensure fields are enabled for rows with data
        const inputs = row.querySelectorAll('input, select, textarea');
        inputs.forEach(function(input) {
          if (input.name && !input.name.includes('-DELETE') && !input.name.includes('-id')) {
            input.disabled = false;
            input.removeAttribute('disabled');
          }
        });
        validRows.push(row);
      }
    });
    
    // Second pass: re-index remaining rows
    validRows.forEach(function(row, index) {
      const newFormIndex = index;
      
      // Check current index of this row
      const firstInput = row.querySelector('input, select, textarea');
      let currentIndex = null;
      if (firstInput && firstInput.name) {
        currentIndex = getFormIndexFromName(firstInput.name);
      }
      
      // Only re-index if index actually changed
      if (currentIndex === newFormIndex) {
        // Index is already correct, just update line number
        const lineNumber = row.querySelector('.line-number');
        if (lineNumber) {
          lineNumber.textContent = (index + 1).toString();
        }
        row.setAttribute('data-form-index', newFormIndex);
        return; // Skip re-indexing for this row
      }
      
      row.setAttribute('data-form-index', newFormIndex);
      
      // Update line number
      const lineNumber = row.querySelector('.line-number');
      if (lineNumber) {
        lineNumber.textContent = (index + 1).toString();
      }
      
      // Log values BEFORE re-indexing
      const itemSelectBefore = row.querySelector('select[name*="-item"]');
      const unitSelectBefore = row.querySelector('select[name*="-unit"]');
      const warehouseSelectBefore = row.querySelector('select[name*="-warehouse"]');
      const quantityInputBefore = row.querySelector('input[name*="-quantity_requested"]');
      
      const valuesBefore = {
        item: itemSelectBefore ? itemSelectBefore.value : 'N/A',
        unit: unitSelectBefore ? unitSelectBefore.value : 'N/A',
        warehouse: warehouseSelectBefore ? warehouseSelectBefore.value : 'N/A',
        quantity: quantityInputBefore ? quantityInputBefore.value : 'N/A'
      };
      
      // Update all input names and IDs (including hidden fields)
      // CRITICAL: Preserve values when changing names
      const allInputs = row.querySelectorAll('input, select, textarea');
      allInputs.forEach(function(input) {
        if (input.name) {
          const oldIndex = getFormIndexFromName(input.name);
          if (oldIndex !== null && oldIndex !== newFormIndex) {
            const oldName = input.name;
            const oldValue = input.value; // Preserve value BEFORE name change
            const oldType = input.type; // Preserve type for checkboxes/radios
            
            // Change name
            input.name = updateFormIndexInName(input.name, newFormIndex);
            
            // CRITICAL: Restore value immediately after name change
            // For select elements, value must match one of the option values
            if (input.tagName === 'SELECT') {
              // For select, check if old value exists in options
              const optionExists = Array.from(input.options).some(opt => opt.value === oldValue);
              if (optionExists && oldValue) {
                input.value = oldValue;
              } else if (oldValue) {
                // If option doesn't exist, try to set it anyway (might be dynamically added)
                input.value = oldValue;
              }
            } else {
              // For input/textarea, just restore the value
              if (oldValue !== null && oldValue !== undefined && oldValue !== '') {
                input.value = oldValue;
              }
            }
            
            // Restore type for checkboxes/radios
            if (oldType) {
              input.type = oldType;
            }
            
            // CRITICAL: Ensure field is enabled after re-indexing
            // Disabled fields won't be submitted!
            input.disabled = false;
            input.removeAttribute('disabled');
            
            // Verify value was preserved
            if (input.value !== oldValue && oldValue) {
              console.error(`⚠️ Value lost during re-index: ${oldName} (${oldValue}) -> ${input.name} (${input.value})`);
            }
          }
        }
        if (input.id) {
          const oldIndex = getFormIndexFromName(input.id);
          if (oldIndex !== null && oldIndex !== newFormIndex) {
            input.id = updateFormIndexInName(input.id, newFormIndex);
          }
        }
      });
      
      // CRITICAL: After re-indexing, ensure all fields in this row are enabled
      // This is important because re-indexing might have affected disabled state
      const allRowInputs = row.querySelectorAll('input, select, textarea');
      const rowDeleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
      const rowIsDeleted = rowDeleteCheckbox && rowDeleteCheckbox.checked;
      
      if (!rowIsDeleted) {
        allRowInputs.forEach(function(input) {
          if (input.name && !input.name.includes('-DELETE') && !input.name.includes('-id')) {
            input.disabled = false;
            input.removeAttribute('disabled');
          }
        });
      }
      
      // Log values AFTER re-indexing to verify they're preserved
      const itemSelectAfter = row.querySelector('select[name*="-item"]');
      const unitSelectAfter = row.querySelector('select[name*="-unit"]');
      const warehouseSelectAfter = row.querySelector('select[name*="-warehouse"]');
      const quantityInputAfter = row.querySelector('input[name*="-quantity_requested"]');
      
      const valuesAfter = {
        item: itemSelectAfter ? itemSelectAfter.value : 'N/A',
        unit: unitSelectAfter ? unitSelectAfter.value : 'N/A',
        warehouse: warehouseSelectAfter ? warehouseSelectAfter.value : 'N/A',
        quantity: quantityInputAfter ? quantityInputAfter.value : 'N/A'
      };
      
      // Warn if values were lost during re-indexing
      if (JSON.stringify(valuesBefore) !== JSON.stringify(valuesAfter)) {
        console.error(`Values lost during re-indexing row ${index}!`);
        console.error('Before:', valuesBefore);
        console.error('After:', valuesAfter);
      }
      
      // Update data-form-index on filter selects
      const filterSelects = row.querySelectorAll('.filter-type-select, .filter-category-select, .filter-subcategory-select, .filter-search-input');
      filterSelects.forEach(function(select) {
        select.setAttribute('data-form-index', newFormIndex);
      });
    });
    
    // Update TOTAL_FORMS
    const finalCount = validRows.length;
    totalFormsInput.value = finalCount.toString();
    
    if (removedCount > 0) {
      console.log(`Removed ${removedCount} empty row(s). Total forms: ${finalCount}`);
    }
    
    return finalCount;
  }

  /**
   * Ensure formset has at least one row with data before form submission
   * Returns true only if at least one row has valid data (item and quantity)
   * NOTE: This function is NOT called during submit anymore to prevent removing valid rows
   */
  function ensureFormsetHasRows(formsetContainer, totalFormsInput) {
    if (!formsetContainer || !totalFormsInput) {
      return false;
    }

    // Check if we have at least one row with data BEFORE removing empty rows
    const rowsBeforeCleanup = formsetContainer.querySelectorAll('.line-row:not(.formset-template)');
    let hasValidRowBefore = false;
    
    rowsBeforeCleanup.forEach(function(row) {
      const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
      const isDeleted = deleteCheckbox && deleteCheckbox.checked;
      
      if (!isDeleted && !isRowEmpty(row)) {
        hasValidRowBefore = true;
      }
    });
    
    // Only remove empty rows if we have at least one valid row
    // This prevents removing rows when user is submitting
    if (!hasValidRowBefore) {
      console.warn('No valid rows found. User must add at least one row with item and quantity.');
      totalFormsInput.value = '0';
      return false;
    }
    
    // Now remove empty rows
    const finalCount = removeEmptyRows(formsetContainer, totalFormsInput);
    
    // Check if we still have at least one row with data after cleanup
    const rows = formsetContainer.querySelectorAll('.line-row:not(.formset-template)');
    let hasValidRow = false;
    
    rows.forEach(function(row) {
      const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
      const isDeleted = deleteCheckbox && deleteCheckbox.checked;
      
      if (!isDeleted && !isRowEmpty(row)) {
        hasValidRow = true;
      }
    });
    
    // IMPORTANT: If no valid rows exist after cleanup, return false
    if (!hasValidRow) {
      console.warn('No valid rows found after cleanup.');
      if (finalCount === 0) {
        totalFormsInput.value = '0';
      }
      return false;
    }
    
    // If we have valid rows, ensure TOTAL_FORMS matches the actual count
    if (hasValidRow && finalCount > 0) {
      totalFormsInput.value = finalCount.toString();
      return true;
    }
    
    return false;
  }

  /**
   * Main initialization function
   */
  function initWarehouseRequestForm() {
    // Initialize Jalali DatePicker
    initJalaliDatePicker();
    
    // Get formset container
    const formsetContainer = document.getElementById('lines-formset');
    if (!formsetContainer) {
      console.warn('Formset container not found');
      return;
    }
    
    // Get total forms input
    const totalFormsInput = document.querySelector('input[name="lines-TOTAL_FORMS"]');
    if (!totalFormsInput) {
      console.warn('TOTAL_FORMS input not found');
      return;
    }
    
    // Add form submit handler to ensure formset has rows before submission
    // CRITICAL: Remove any existing handler first to prevent duplicate handlers
    const form = formsetContainer.closest('form');
    if (form) {
      // Remove existing handler if it exists (by cloning the form to remove all listeners)
      // Actually, we can't easily remove anonymous handlers, so we'll use a flag instead
      if (form.dataset.submitHandlerAdded === 'true') {
        console.warn('Submit handler already added, skipping...');
        return;
      }
      form.dataset.submitHandlerAdded = 'true';
      
      // Add a bubble phase listener that runs AFTER capture phase handlers
      // This ensures fields stay enabled even if other handlers disable them
      form.addEventListener('submit', function(e) {
        // Enable all fields one last time in bubble phase (runs after capture phase)
        const allRowsBubble = formsetContainer.querySelectorAll('.line-row:not(.formset-template)');
        allRowsBubble.forEach(function(row) {
          const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
          const isDeleted = deleteCheckbox && deleteCheckbox.checked;
          
          if (!isDeleted) {
            const inputs = row.querySelectorAll('input, select, textarea');
            inputs.forEach(function(input) {
              if (input.name && !input.name.includes('-DELETE')) {
                input.disabled = false;
                input.removeAttribute('disabled');
              }
            });
          }
        });
        
        // Enable main form fields
        const mainFormInputsBubble = form.querySelectorAll('input, select, textarea');
        mainFormInputsBubble.forEach(function(input) {
          if (input.name && !input.name.startsWith('lines-')) {
            input.disabled = false;
            input.removeAttribute('disabled');
          }
        });
        
        // Enable TOTAL_FORMS
        totalFormsInput.disabled = false;
        totalFormsInput.removeAttribute('disabled');
      }, false); // Bubble phase - runs AFTER capture phase handlers
      
      // Main submit handler in capture phase (runs FIRST)
      form.addEventListener('submit', function(e) {
        console.log('🚀 SUBMIT HANDLER TRIGGERED (capture phase)');
        
        // CRITICAL: Enable ALL form fields FIRST before any processing
        // Disabled fields are NOT included in form submission!
        // This includes both formset fields AND main form fields
        
        // 1. Enable all formset fields FIRST
        const allRowsBefore = formsetContainer.querySelectorAll('.line-row:not(.formset-template)');
        console.log(`📊 Total rows found: ${allRowsBefore.length}`);
        
        allRowsBefore.forEach(function(row, idx) {
          const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
          const isDeleted = deleteCheckbox && deleteCheckbox.checked;
          
          if (!isDeleted) {
            const inputs = row.querySelectorAll('input, select, textarea');
            inputs.forEach(function(input) {
              // Enable all fields except DELETE checkboxes and hidden ID fields
              if (input.name && !input.name.includes('-DELETE') && !input.name.includes('-id')) {
                input.removeAttribute('disabled');
                input.disabled = false;
              }
            });
          }
        });
        
        // 2. Enable all main form fields
        const mainFormInputs = form.querySelectorAll('input, select, textarea');
        mainFormInputs.forEach(function(input) {
          if (input.name && !input.name.startsWith('lines-')) {
            input.removeAttribute('disabled');
            input.disabled = false;
          }
        });
        
        // 3. Enable TOTAL_FORMS input
        totalFormsInput.removeAttribute('disabled');
        totalFormsInput.disabled = false;
        
        // Now count valid rows AFTER enabling fields
        let validRowCountBefore = 0;
        let debugRows = [];
        allRowsBefore.forEach(function(row, idx) {
          const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
          const isDeleted = deleteCheckbox && deleteCheckbox.checked;
          const isEmpty = isRowEmpty(row);
          
          const itemSelect = row.querySelector('select[name*="-item"]');
          const quantityInput = row.querySelector('input[name*="-quantity_requested"]');
          const warehouseSelect = row.querySelector('select[name*="-warehouse"]');
          const unitSelect = row.querySelector('select[name*="-unit"]');
          
          const itemValue = itemSelect ? itemSelect.value : '';
          const quantityValue = quantityInput ? quantityInput.value : '';
          const warehouseValue = warehouseSelect ? warehouseSelect.value : '';
          const unitValue = unitSelect ? unitSelect.value : '';
          const itemName = itemSelect ? itemSelect.name : 'N/A';
          const itemDisabled = itemSelect ? itemSelect.disabled : false;
          
          debugRows.push({
            idx: idx,
            deleted: isDeleted,
            empty: isEmpty,
            item: itemValue,
            quantity: quantityValue,
            warehouse: warehouseValue,
            unit: unitValue,
            itemName: itemName,
            itemDisabled: itemDisabled
          });
          
          if (!isDeleted && !isEmpty) {
            validRowCountBefore++;
          }
        });
        
        console.log('=== DEBUG INFO (after enabling fields) ===');
        console.log(`Valid rows: ${validRowCountBefore}`);
        console.log('Row details:');
        debugRows.forEach(function(r) {
          console.log(`  Row ${r.idx}: deleted=${r.deleted}, empty=${r.empty}, item="${r.item}", qty="${r.quantity}", wh="${r.warehouse}", unit="${r.unit}", name="${r.itemName}", disabled=${r.itemDisabled}`);
        });
        
        // Only remove empty rows if we have at least one valid row
        // This prevents removing rows when user is submitting
        if (validRowCountBefore === 0) {
          e.preventDefault();
          e.stopPropagation();
          console.error('❌ No valid rows found! Preventing submit.');
          alert('خطا: هیچ ردیف معتبری پیدا نشد. لطفاً حداقل یک ردیف با کالا و مقدار به فرم اضافه کنید.');
          return false;
        }
        
        // 2. Enable all main form fields (department_unit, needed_by_date, priority, purpose, approver)
        const mainFormInputsAfter = form.querySelectorAll('input, select, textarea');
        let mainFormFieldsCount = 0;
        mainFormInputsAfter.forEach(function(input) {
          // Only enable fields that are NOT part of formset
          if (input.name && !input.name.startsWith('lines-')) {
            input.removeAttribute('disabled');
            input.disabled = false;
            mainFormFieldsCount++;
            console.log(`Enabled main form field: ${input.name} = ${input.value}`);
          }
        });
        console.log(`Total main form fields enabled: ${mainFormFieldsCount}`);
        
        // CRITICAL: Don't call ensureFormsetHasRows if we already have valid rows
        // It might remove rows incorrectly. Instead, just ensure TOTAL_FORMS is correct
        // and enable all fields
        
        // Get all rows after enabling fields
        const rowsAfterEnable = formsetContainer.querySelectorAll('.line-row:not(.formset-template)');
        
        // CRITICAL: Update TOTAL_FORMS FIRST before counting rows
        // Make sure the input is enabled and not disabled
        totalFormsInput.disabled = false;
        totalFormsInput.removeAttribute('disabled');
        const totalFormsBefore = parseInt(totalFormsInput.value) || 0;
        totalFormsInput.value = rowsAfterEnable.length.toString();
        const totalFormsAfter = parseInt(totalFormsInput.value) || 0;
        
        // Count valid rows
        let validRowCountAfter = 0;
        let debugInfoAfter = '=== AFTER ENABLE FIELDS ===\n';
        debugInfoAfter += `Total rows: ${rowsAfterEnable.length}\n`;
        debugInfoAfter += `TOTAL_FORMS (before): ${totalFormsBefore}\n`;
        debugInfoAfter += `TOTAL_FORMS (after): ${totalFormsAfter}\n\n`;
        
        rowsAfterEnable.forEach(function(row, idx) {
          const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
          const isDeleted = deleteCheckbox && deleteCheckbox.checked;
          const isEmpty = isRowEmpty(row);
          
          const itemSelect = row.querySelector('select[name*="-item"]');
          const quantityInput = row.querySelector('input[name*="-quantity_requested"]');
          const warehouseSelect = row.querySelector('select[name*="-warehouse"]');
          const unitSelect = row.querySelector('select[name*="-unit"]');
          
          const itemValue = itemSelect ? itemSelect.value : '';
          const quantityValue = quantityInput ? quantityInput.value : '';
          const warehouseValue = warehouseSelect ? warehouseSelect.value : '';
          const unitValue = unitSelect ? unitSelect.value : '';
          const itemName = itemSelect ? itemSelect.name : 'N/A';
          const itemDisabled = itemSelect ? itemSelect.disabled : false;
          
          debugInfoAfter += `Row ${idx}: deleted=${isDeleted}, empty=${isEmpty}, item="${itemValue}", qty="${quantityValue}", wh="${warehouseValue}", unit="${unitValue}", name="${itemName}", disabled=${itemDisabled}\n`;
          
          if (!isDeleted && !isEmpty) {
            validRowCountAfter++;
          }
        });
        
        debugInfoAfter += `\nValid rows: ${validRowCountAfter}\n`;
        
        // Log debug info to console (don't use alert - it blocks execution)
        console.log('=== AFTER ENABLE FIELDS ===');
        console.log(debugInfoAfter);
        
        // Final validation checks
        if (validRowCountAfter === 0) {
          e.preventDefault();
          e.stopPropagation();
          alert('خطا: هیچ ردیف معتبری پیدا نشد. لطفاً حداقل یک ردیف با کالا و مقدار به فرم اضافه کنید.');
          return false;
        }
        
        // CRITICAL: Double-check TOTAL_FORMS one more time before submit
        // Make sure it's enabled and has the correct value
        totalFormsInput.disabled = false;
        totalFormsInput.removeAttribute('disabled');
        const finalTotalForms = parseInt(totalFormsInput.value) || 0;
        
        if (finalTotalForms === 0) {
          // Force set it again
          totalFormsInput.value = rowsAfterEnable.length.toString();
          const forcedTotalForms = parseInt(totalFormsInput.value) || 0;
          if (forcedTotalForms === 0) {
            e.preventDefault();
            e.stopPropagation();
            alert(`خطا: TOTAL_FORMS صفر است و نمی‌توان آن را تنظیم کرد. ردیف‌ها: ${rowsAfterEnable.length}`);
            return false;
          }
        }
        
        if (finalTotalForms !== rowsAfterEnable.length) {
          // Fix TOTAL_FORMS
          totalFormsInput.value = rowsAfterEnable.length.toString();
          alert(`توجه: TOTAL_FORMS اصلاح شد از ${finalTotalForms} به ${rowsAfterEnable.length}`);
        }
        
        // FINAL CHECK: Ensure ALL form fields (formset + main form) are enabled before submit
        // This is critical because disabled fields are NOT submitted!
        
        // 1. Enable all formset fields one more time (in case removeEmptyRows disabled them)
        rowsAfterEnable.forEach(function(row, idx) {
          const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
          const isDeleted = deleteCheckbox && deleteCheckbox.checked;
          
          if (!isDeleted) {
            const inputs = row.querySelectorAll('input, select, textarea');
            inputs.forEach(function(input) {
              if (input.name && !input.name.includes('-DELETE')) {
                input.disabled = false;
                input.removeAttribute('disabled');
              }
            });
          }
        });
        
        // 2. Enable all main form fields one more time
        const mainFormInputsFinal = form.querySelectorAll('input, select, textarea');
        let mainFormFieldsEnabled = 0;
        mainFormInputsFinal.forEach(function(input) {
          if (input.name && !input.name.startsWith('lines-')) {
            input.disabled = false;
            input.removeAttribute('disabled');
            mainFormFieldsEnabled++;
            console.log(`Enabled main form field: ${input.name} = ${input.value}`);
          }
        });
        console.log(`Total main form fields enabled: ${mainFormFieldsEnabled}`);
        
        // 3. Validate formset fields have values
        let hasValidationError = false;
        rowsAfterEnable.forEach(function(row, idx) {
          const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
          const isDeleted = deleteCheckbox && deleteCheckbox.checked;
          
          if (!isDeleted) {
            
            // Log field values for debugging
            const itemSelect = row.querySelector('select[name*="-item"]');
            const unitSelect = row.querySelector('select[name*="-unit"]');
            const quantityInput = row.querySelector('input[name*="-quantity_requested"]');
            const warehouseSelect = row.querySelector('select[name*="-warehouse"]');
            
            const fieldValues = {
              item: itemSelect ? itemSelect.value : 'N/A',
              unit: unitSelect ? unitSelect.value : 'N/A',
              quantity: quantityInput ? quantityInput.value : 'N/A',
              warehouse: warehouseSelect ? warehouseSelect.value : 'N/A',
              itemName: itemSelect ? itemSelect.name : 'N/A',
              unitName: unitSelect ? unitSelect.name : 'N/A',
              quantityName: quantityInput ? quantityInput.name : 'N/A',
              warehouseName: warehouseSelect ? warehouseSelect.name : 'N/A',
              itemDisabled: itemSelect ? itemSelect.disabled : 'N/A',
              unitDisabled: unitSelect ? unitSelect.disabled : 'N/A',
              quantityDisabled: quantityInput ? quantityInput.disabled : 'N/A',
              warehouseDisabled: warehouseSelect ? warehouseSelect.disabled : 'N/A'
            };
            
            console.log(`Row ${idx} final values before submit:`, fieldValues);
            
            // Validate that required fields have values
            if (!fieldValues.item || fieldValues.item === '' || fieldValues.item === 'N/A') {
              console.error(`Row ${idx}: Item field is empty! Name: ${fieldValues.itemName}, Value: ${fieldValues.item}`);
              hasValidationError = true;
            }
            if (!fieldValues.quantity || fieldValues.quantity === '' || fieldValues.quantity === 'N/A' || parseFloat(fieldValues.quantity) <= 0) {
              console.error(`Row ${idx}: Quantity field is empty or invalid! Name: ${fieldValues.quantityName}, Value: ${fieldValues.quantity}`);
              hasValidationError = true;
            }
            if (!fieldValues.warehouse || fieldValues.warehouse === '' || fieldValues.warehouse === 'N/A') {
              console.error(`Row ${idx}: Warehouse field is empty! Name: ${fieldValues.warehouseName}, Value: ${fieldValues.warehouse}`);
              hasValidationError = true;
            }
            
            // Check if fields are disabled (they won't be submitted)
            if (fieldValues.itemDisabled || fieldValues.unitDisabled || fieldValues.warehouseDisabled || fieldValues.quantityDisabled) {
              console.error(`Row ${idx}: Some fields are disabled and won't be submitted!`);
              console.error('  Item disabled:', fieldValues.itemDisabled);
              console.error('  Unit disabled:', fieldValues.unitDisabled);
              console.error('  Warehouse disabled:', fieldValues.warehouseDisabled);
              console.error('  Quantity disabled:', fieldValues.quantityDisabled);
              hasValidationError = true;
            }
          }
        });
        
        if (hasValidationError) {
          e.preventDefault();
          e.stopPropagation();
          console.error('Validation failed: Required fields are missing or disabled');
          alert('خطا: برخی فیلدهای لازم خالی هستند یا غیرفعال شده‌اند. لطفاً فرم را بررسی کنید.');
          return false;
        }
        
        // FINAL FINAL CHECK: Ensure TOTAL_FORMS is correct one last time
        totalFormsInput.disabled = false;
        totalFormsInput.removeAttribute('disabled');
        const finalCheckTotalForms = parseInt(totalFormsInput.value) || 0;
        if (finalCheckTotalForms !== rowsAfterEnable.length) {
          totalFormsInput.value = rowsAfterEnable.length.toString();
          alert(`⚠️ توجه: TOTAL_FORMS در آخرین لحظه اصلاح شد از ${finalCheckTotalForms} به ${rowsAfterEnable.length}`);
        }
        
        // Verify TOTAL_FORMS is not 0
        const veryFinalTotalForms = parseInt(totalFormsInput.value) || 0;
        if (veryFinalTotalForms === 0) {
          e.preventDefault();
          e.stopPropagation();
          alert(`❌ خطا: TOTAL_FORMS هنوز صفر است! ردیف‌ها: ${rowsAfterEnable.length}`);
          return false;
        }
        
        // ABSOLUTE FINAL CHECK: Enable ALL fields one last time before submit
        // This is critical - disabled fields are NOT submitted!
        rowsAfterEnable.forEach(function(row) {
          const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
          const isDeleted = deleteCheckbox && deleteCheckbox.checked;
          
          if (!isDeleted) {
            const inputs = row.querySelectorAll('input, select, textarea');
            inputs.forEach(function(input) {
              if (input.name && !input.name.includes('-DELETE')) {
                input.disabled = false;
                input.removeAttribute('disabled');
              }
            });
          }
        });
        
        // Enable all main form fields one last time
        const allMainFormInputs = form.querySelectorAll('input, select, textarea');
        allMainFormInputs.forEach(function(input) {
          if (input.name && !input.name.startsWith('lines-')) {
            input.disabled = false;
            input.removeAttribute('disabled');
          }
        });
        
        // Enable TOTAL_FORMS input
        totalFormsInput.disabled = false;
        totalFormsInput.removeAttribute('disabled');
        
        // Log final state before submit
        let finalDebugInfo = '=== FINAL STATE BEFORE SUBMIT ===\n';
        finalDebugInfo += `TOTAL_FORMS: ${totalFormsInput.value}\n`;
        finalDebugInfo += `Total rows: ${rowsAfterEnable.length}\n\n`;
        
        rowsAfterEnable.forEach(function(row, idx) {
          const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
          const isDeleted = deleteCheckbox && deleteCheckbox.checked;
          
          if (!isDeleted) {
            const itemSelect = row.querySelector('select[name*="-item"]');
            const quantityInput = row.querySelector('input[name*="-quantity_requested"]');
            const warehouseSelect = row.querySelector('select[name*="-warehouse"]');
            const unitSelect = row.querySelector('select[name*="-unit"]');
            
            finalDebugInfo += `Row ${idx}:\n`;
            finalDebugInfo += `  item: "${itemSelect ? itemSelect.value : ''}" (name: ${itemSelect ? itemSelect.name : 'N/A'}, disabled: ${itemSelect ? itemSelect.disabled : 'N/A'})\n`;
            finalDebugInfo += `  quantity: "${quantityInput ? quantityInput.value : ''}" (name: ${quantityInput ? quantityInput.name : 'N/A'}, disabled: ${quantityInput ? quantityInput.disabled : 'N/A'})\n`;
            finalDebugInfo += `  warehouse: "${warehouseSelect ? warehouseSelect.value : ''}" (name: ${warehouseSelect ? warehouseSelect.name : 'N/A'}, disabled: ${warehouseSelect ? warehouseSelect.disabled : 'N/A'})\n`;
            finalDebugInfo += `  unit: "${unitSelect ? unitSelect.value : ''}" (name: ${unitSelect ? unitSelect.name : 'N/A'}, disabled: ${unitSelect ? unitSelect.disabled : 'N/A'})\n\n`;
          }
        });
        
        // Log final debug info to console (don't use alert - it blocks execution)
        console.log('=== FINAL STATE BEFORE SUBMIT ===');
        console.log(finalDebugInfo);
        
        // CRITICAL: Final enable right before submit (no alert blocking)
        rowsAfterEnable.forEach(function(row) {
          const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
          const isDeleted = deleteCheckbox && deleteCheckbox.checked;
          
          if (!isDeleted) {
            const inputs = row.querySelectorAll('input, select, textarea');
            inputs.forEach(function(input) {
              if (input.name && !input.name.includes('-DELETE')) {
                // CRITICAL: Remove disabled attribute completely (not set to 'false')
                input.removeAttribute('disabled');
                input.disabled = false;
              }
            });
          }
        });
        
        // Enable main form fields one more time
        const allMainFormInputsFinal = form.querySelectorAll('input, select, textarea');
        allMainFormInputsFinal.forEach(function(input) {
          if (input.name && !input.name.startsWith('lines-')) {
            // CRITICAL: Remove disabled attribute completely (not set to 'false')
            input.removeAttribute('disabled');
            input.disabled = false;
          }
        });
        
        // Enable TOTAL_FORMS one more time
        totalFormsInput.removeAttribute('disabled');
        totalFormsInput.disabled = false;
        
        // Verify all fields are enabled
        let allFieldsEnabled = true;
        rowsAfterEnable.forEach(function(row) {
          const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
          const isDeleted = deleteCheckbox && deleteCheckbox.checked;
          
          if (!isDeleted) {
            const itemSelect = row.querySelector('select[name*="-item"]');
            const quantityInput = row.querySelector('input[name*="-quantity_requested"]');
            const warehouseSelect = row.querySelector('select[name*="-warehouse"]');
            
            if (itemSelect && itemSelect.disabled) {
              console.error('Item field is still disabled!');
              allFieldsEnabled = false;
            }
            if (quantityInput && quantityInput.disabled) {
              console.error('Quantity field is still disabled!');
              allFieldsEnabled = false;
            }
            if (warehouseSelect && warehouseSelect.disabled) {
              console.error('Warehouse field is still disabled!');
              allFieldsEnabled = false;
            }
          }
        });
        
        if (!allFieldsEnabled) {
          console.error('Some fields are still disabled! Forcing enable...');
          // Force enable one more time
          rowsAfterEnable.forEach(function(row) {
            const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
            const isDeleted = deleteCheckbox && deleteCheckbox.checked;
            
            if (!isDeleted) {
              const inputs = row.querySelectorAll('input, select, textarea');
              inputs.forEach(function(input) {
                if (input.name && !input.name.includes('-DELETE')) {
                  input.disabled = false;
                  input.removeAttribute('disabled');
                }
              });
            }
          });
        }
        
        // FINAL VERIFICATION: Check that fields have values before submit
        let hasEmptyFields = false;
        rowsAfterEnable.forEach(function(row, idx) {
          const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
          const isDeleted = deleteCheckbox && deleteCheckbox.checked;
          
          if (!isDeleted) {
            const itemSelect = row.querySelector('select[name*="-item"]');
            const quantityInput = row.querySelector('input[name*="-quantity_requested"]');
            const warehouseSelect = row.querySelector('select[name*="-warehouse"]');
            const unitSelect = row.querySelector('select[name*="-unit"]');
            
            const itemValue = itemSelect ? itemSelect.value : '';
            const quantityValue = quantityInput ? quantityInput.value : '';
            const warehouseValue = warehouseSelect ? warehouseSelect.value : '';
            const unitValue = unitSelect ? unitSelect.value : '';
            
            if (!itemValue || !quantityValue || !warehouseValue || !unitValue) {
              console.error(`Row ${idx} has empty fields: item="${itemValue}", qty="${quantityValue}", wh="${warehouseValue}", unit="${unitValue}"`);
              hasEmptyFields = true;
            }
            
            // Also check if fields are disabled
            if (itemSelect && itemSelect.disabled) {
              console.error(`Row ${idx}: Item field is disabled!`);
              hasEmptyFields = true;
            }
            if (quantityInput && quantityInput.disabled) {
              console.error(`Row ${idx}: Quantity field is disabled!`);
              hasEmptyFields = true;
            }
            if (warehouseSelect && warehouseSelect.disabled) {
              console.error(`Row ${idx}: Warehouse field is disabled!`);
              hasEmptyFields = true;
            }
          }
        });
        
        if (hasEmptyFields) {
          e.preventDefault();
          e.stopPropagation();
          console.error('❌ Validation failed: Some fields are empty or disabled!');
          alert('خطا: برخی فیلدها خالی هستند یا غیرفعال شده‌اند. لطفاً فرم را بررسی کنید.');
          return false;
        }
        
        console.log('=== Form Validation Passed. Submitting... ===');
        console.log(`Final TOTAL_FORMS: ${veryFinalTotalForms}, Rows: ${rowsAfterEnable.length}`);
        console.log(`All fields enabled: ${allFieldsEnabled}`);
        
        // CRITICAL FIX: Use FormData to manually collect values and submit
        // This ensures values are sent even if fields get disabled by other handlers
        const formData = new FormData(form);
        
        // Manually add formset field values to ensure they're included
        rowsAfterEnable.forEach(function(row, idx) {
          const deleteCheckbox = row.querySelector('input[type="checkbox"][name*="-DELETE"]');
          const isDeleted = deleteCheckbox && deleteCheckbox.checked;
          
          if (!isDeleted) {
            const itemSelect = row.querySelector('select[name*="-item"]');
            const quantityInput = row.querySelector('input[name*="-quantity_requested"]');
            const warehouseSelect = row.querySelector('select[name*="-warehouse"]');
            const unitSelect = row.querySelector('select[name*="-unit"]');
            const lineNotesInput = row.querySelector('textarea[name*="-line_notes"]');
            
            if (itemSelect && itemSelect.value) {
              formData.set(itemSelect.name, itemSelect.value);
              console.log(`✅ Manually added to FormData: ${itemSelect.name} = ${itemSelect.value}`);
            }
            if (quantityInput && quantityInput.value) {
              formData.set(quantityInput.name, quantityInput.value);
              console.log(`✅ Manually added to FormData: ${quantityInput.name} = ${quantityInput.value}`);
            }
            if (warehouseSelect && warehouseSelect.value) {
              formData.set(warehouseSelect.name, warehouseSelect.value);
              console.log(`✅ Manually added to FormData: ${warehouseSelect.name} = ${warehouseSelect.value}`);
            }
            if (unitSelect && unitSelect.value) {
              formData.set(unitSelect.name, unitSelect.value);
              console.log(`✅ Manually added to FormData: ${unitSelect.name} = ${unitSelect.value}`);
            }
            if (lineNotesInput) {
              formData.set(lineNotesInput.name, lineNotesInput.value || '');
            }
          }
        });
        
        // Ensure TOTAL_FORMS is set correctly
        formData.set('lines-TOTAL_FORMS', veryFinalTotalForms.toString());
        console.log(`✅ Manually set TOTAL_FORMS in FormData: ${veryFinalTotalForms}`);
        
        // Prevent default form submission
        e.preventDefault();
        e.stopPropagation();
        
        // Submit form using fetch API with FormData
        fetch(form.action || window.location.href, {
          method: 'POST',
          body: formData,
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        }).then(function(response) {
          if (response.redirected) {
            window.location.href = response.url;
          } else {
            return response.text().then(function(html) {
              document.open();
              document.write(html);
              document.close();
            });
          }
        }).catch(function(error) {
          console.error('Form submission error:', error);
          alert('خطا در ارسال فرم. لطفاً دوباره تلاش کنید.');
        });
        
        return false;
      }, true); // Use capture phase to run BEFORE other handlers
    }
    
    // Check if formset is empty (TOTAL_FORMS = 0)
    // This should not happen if formset is properly initialized with extra=1
    if (parseInt(totalFormsInput.value) === 0) {
      console.error('Formset is empty! TOTAL_FORMS = 0. This should not happen.');
      console.error('Formset should have at least 1 empty row (extra=1).');
      console.error('Attempting to create a template row manually...');
      
      // Try to create a template row from the header structure
      // This is a workaround for when formset is not properly initialized
      const header = formsetContainer.querySelector('.lines-table-header');
      if (header) {
        // Create a basic row structure matching the template structure
        const templateRow = document.createElement('div');
        templateRow.className = 'line-row';
        templateRow.setAttribute('data-form-index', '0');
        
        // Number cell
        const numberCell = document.createElement('div');
        numberCell.className = 'line-cell line-number';
        numberCell.textContent = '1';
        templateRow.appendChild(numberCell);
        
        // Item cell with filters
        const itemCell = document.createElement('div');
        itemCell.className = 'line-cell line-item';
        const itemWrapper = document.createElement('div');
        itemWrapper.className = 'item-select-wrapper';
        const itemFilters = document.createElement('div');
        itemFilters.className = 'item-filters';
        itemFilters.innerHTML = `
          <select class="form-control filter-type-select" data-form-index="0">
            <option value="">Type</option>
          </select>
          <select class="form-control filter-category-select" data-form-index="0">
            <option value="">Category</option>
          </select>
          <select class="form-control filter-subcategory-select" data-form-index="0">
            <option value="">Subcategory</option>
          </select>
          <input type="text" class="form-control filter-search-input" data-form-index="0" placeholder="Search by name or code...">
        `;
        const itemSelect = document.createElement('select');
        itemSelect.name = 'lines-0-item';
        itemSelect.id = 'id_lines-0-item';
        itemSelect.className = 'form-control';
        itemSelect.innerHTML = '<option value="">--- انتخاب کنید ---</option>';
        itemWrapper.appendChild(itemFilters);
        itemWrapper.appendChild(itemSelect);
        itemCell.appendChild(itemWrapper);
        templateRow.appendChild(itemCell);
        
        // Unit cell
        const unitCell = document.createElement('div');
        unitCell.className = 'line-cell line-unit';
        const unitSelect = document.createElement('select');
        unitSelect.name = 'lines-0-unit';
        unitSelect.id = 'id_lines-0-unit';
        unitSelect.className = 'form-control';
        unitSelect.innerHTML = '<option value="">--- انتخاب کنید ---</option>';
        unitCell.appendChild(unitSelect);
        templateRow.appendChild(unitCell);
        
        // Quantity cell
        const quantityCell = document.createElement('div');
        quantityCell.className = 'line-cell line-quantity';
        const quantityInput = document.createElement('input');
        quantityInput.type = 'number';
        quantityInput.name = 'lines-0-quantity_requested';
        quantityInput.id = 'id_lines-0-quantity_requested';
        quantityInput.className = 'form-control';
        quantityInput.step = '0.01';
        quantityCell.appendChild(quantityInput);
        templateRow.appendChild(quantityCell);
        
        // Warehouse cell
        const warehouseCell = document.createElement('div');
        warehouseCell.className = 'line-cell line-warehouse';
        const warehouseSelect = document.createElement('select');
        warehouseSelect.name = 'lines-0-warehouse';
        warehouseSelect.id = 'id_lines-0-warehouse';
        warehouseSelect.className = 'form-control';
        warehouseSelect.innerHTML = '<option value="">--- انتخاب کنید ---</option>';
        warehouseCell.appendChild(warehouseSelect);
        templateRow.appendChild(warehouseCell);
        
        // Notes cell
        const notesCell = document.createElement('div');
        notesCell.className = 'line-cell line-notes';
        const notesInput = document.createElement('input');
        notesInput.type = 'text';
        notesInput.name = 'lines-0-line_notes';
        notesInput.id = 'id_lines-0-line_notes';
        notesInput.className = 'form-control';
        notesCell.appendChild(notesInput);
        templateRow.appendChild(notesCell);
        
        // Delete cell (if can_delete)
        const canDelete = formsetContainer.getAttribute('data-can-delete') === 'true';
        if (canDelete) {
          const deleteCell = document.createElement('div');
          deleteCell.className = 'line-cell line-delete';
          const deleteCheckbox = document.createElement('input');
          deleteCheckbox.type = 'checkbox';
          deleteCheckbox.name = 'lines-0-DELETE';
          deleteCheckbox.id = 'id_lines-0-DELETE';
          deleteCheckbox.className = 'form-check-input';
          deleteCell.appendChild(deleteCheckbox);
          templateRow.appendChild(deleteCell);
        }
        
        // Add hidden fields (Django formset requires these)
        // Note: For new forms, id should be empty string, not missing
        const hiddenId = document.createElement('input');
        hiddenId.type = 'hidden';
        hiddenId.name = 'lines-0-id';
        hiddenId.id = 'id_lines-0-id';
        hiddenId.value = ''; // Empty for new forms
        templateRow.insertBefore(hiddenId, templateRow.firstChild); // Insert at beginning
        
        // Insert after header
        formsetContainer.insertBefore(templateRow, header.nextSibling);
        totalFormsInput.value = '1';
        console.log('Created manual template row. TOTAL_FORMS set to 1.');
        
        // Apply layout immediately
        applyFormsetLayout(formsetContainer);
        
        // Initialize filters for the manually created row
        const filterOptions = {
          placeholder: "--- انتخاب کنید ---",
          allCategoriesText: "همه دسته‌بندی‌ها",
          allSubcategoriesText: "همه زیردسته‌بندی‌ها",
        };
        
        // Wait a bit then initialize filters
        setTimeout(function() {
          if (typeof initializeItemFiltersForRow === 'function') {
            initializeItemFiltersForRow(templateRow, filterOptions);
          }
        }, 50);
      } else {
        console.error('Cannot create template row - header not found.');
        return;
      }
    }
    
    // FIRST: Remove extra empty rows immediately (before any other initialization)
    // Use requestAnimationFrame to ensure DOM is fully ready
    requestAnimationFrame(function() {
      removeExtraRows(formsetContainer, totalFormsInput);
      
      // Apply grid layout immediately after removing rows
      applyFormsetLayout(formsetContainer);
    });
    
    // Configuration for item filters
    const filterOptions = {
      placeholder: "--- انتخاب کنید ---",
      allCategoriesText: "همه دسته‌بندی‌ها",
      allSubcategoriesText: "همه زیردسته‌بندی‌ها",
    };
    
    // Wait a bit for DOM to be fully ready, then initialize
    setTimeout(function() {
      // Check again if formset has rows
      const rows = formsetContainer.querySelectorAll('.line-row:not(.formset-template)');
      if (rows.length === 0) {
        console.error('Still no rows found after timeout. Formset initialization failed.');
        return;
      }
      
      // Initialize item filters for existing rows
      initializeLineForms(formsetContainer, filterOptions);
      
      // Handle add line button - use formset.js
      const addLineBtn = document.getElementById('add-line-btn');
      initFormsetManagement(formsetContainer, addLineBtn, totalFormsInput, filterOptions);
      
      // Handle delete checkboxes
      initDeleteCheckboxes(formsetContainer, filterOptions);
      
      // Final layout check
      applyFormsetLayout(formsetContainer);
    }, 150);
  }

  // Initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWarehouseRequestForm);
  } else {
    initWarehouseRequestForm();
  }

})();

