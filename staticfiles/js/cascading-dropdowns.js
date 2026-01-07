/**
 * Cascading dropdown utilities for dependent select fields.
 * 
 * This file provides functions for managing cascading dropdowns where
 * the options in one dropdown depend on the selection in another.
 */

/**
 * Initialize cascading dropdown.
 * 
 * @param {string|HTMLElement} parentSelect - Parent dropdown element or selector
 * @param {string|HTMLElement} childSelect - Child dropdown element or selector
 * @param {string} apiUrl - API endpoint URL (e.g., '/api/categories/')
 * @param {Object} options - Configuration options
 * @param {string} options.parentField - Parent field name for API (e.g., 'item_type_id')
 * @param {string} options.placeholder - Placeholder text for child dropdown
 * @param {string} options.valueField - Field name for option value (default: 'id')
 * @param {string} options.labelField - Field name for option label (default: 'name')
 * @param {Function} options.onChange - Callback function when child changes
 * @param {Function} options.onError - Callback function for API errors
 */
function initCascadingDropdown(parentSelect, childSelect, apiUrl, options = {}) {
    const parentElement = typeof parentSelect === 'string' 
        ? document.querySelector(parentSelect) 
        : parentSelect;
    const childElement = typeof childSelect === 'string' 
        ? document.querySelector(childSelect) 
        : childSelect;
    
    if (!parentElement || !childElement) {
        console.error('Parent or child select element not found');
        return;
    }
    
    const config = {
        parentField: options.parentField || 'parent_id',
        placeholder: options.placeholder || '--- Select ---',
        valueField: options.valueField || 'id',
        labelField: options.labelField || 'name',
        onChange: options.onChange || null,
        onError: options.onError || null,
    };
    
    // Store config on child element for later use
    childElement.dataset.cascadingConfig = JSON.stringify({
        apiUrl,
        ...config
    });
    childElement.dataset.parentSelector = parentElement.id || parentElement.name;
    
    // Listen to parent change
    parentElement.addEventListener('change', function() {
        const parentValue = this.value;
        
        if (!parentValue) {
            // Clear child dropdown
            clearDropdown(childElement, config.placeholder);
            return;
        }
        
        // Save current value and text before clearing (important for warehouses)
        const currentValue = childElement.value;
        let currentOptionText = null;
        if (currentValue) {
            const existingOption = Array.from(childElement.options).find(opt => opt.value === currentValue || opt.value == currentValue);
            if (existingOption) {
                currentOptionText = existingOption.textContent;
            }
        }
        // Also check data-initial-value attribute
        if (!currentValue && childElement.hasAttribute('data-initial-value')) {
            const initialValue = childElement.getAttribute('data-initial-value');
            const existingOption = Array.from(childElement.options).find(opt => opt.value === initialValue || opt.value == initialValue);
            if (existingOption) {
                currentOptionText = existingOption.textContent;
            }
        }
        
        // Show loading state
        childElement.disabled = true;
        const originalHTML = childElement.innerHTML;
        childElement.innerHTML = `<option value="">${config.placeholder}...</option>`;
        
        // Fetch options from API
        const url = new URL(apiUrl, window.location.origin);
        url.searchParams.set(config.parentField, parentValue);
        
        fetch(url.toString(), {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Handle different response formats
            let options = [];
            if (Array.isArray(data)) {
                options = data;
            } else if (data.results && Array.isArray(data.results)) {
                options = data.results;
            } else if (data.data && Array.isArray(data.data)) {
                options = data.data;
            } else if (data.units && Array.isArray(data.units)) {
                // Support for item_allowed_units API format
                options = data.units;
            } else if (data.warehouses && Array.isArray(data.warehouses)) {
                // Support for item_allowed_warehouses API format
                options = data.warehouses;
            } else if (data.sub_accounts && Array.isArray(data.sub_accounts)) {
                // Support for treasury_account_api_sub_accounts API format
                // Transform to standard format: {id, label: code + ' · ' + name}
                options = data.sub_accounts.map(function(acc) {
                    return {
                        id: acc.id,
                        value: acc.id,
                        name: acc.code + ' · ' + acc.name,
                        label: acc.code + ' · ' + acc.name
                    };
                });
            } else if (data.gl_accounts && Array.isArray(data.gl_accounts)) {
                // Support for treasury_account_api_gl_accounts API format
                // Transform to standard format: {id, label: code + ' · ' + name, is_primary}
                options = data.gl_accounts.map(function(acc) {
                    return {
                        id: acc.id,
                        value: acc.id,
                        name: acc.code + ' · ' + acc.name,
                        label: acc.code + ' · ' + acc.name,
                        is_primary: acc.is_primary
                    };
                });
            } else {
                console.warn('Unexpected API response format:', data);
                options = [];
            }
            
            // Check if current value is in the options list (for warehouses)
            const isWarehouseDropdown = data.warehouses !== undefined;
            let currentValueInList = false;
            if (isWarehouseDropdown && currentValue) {
                currentValueInList = options.some(opt => {
                    const optValue = opt.value || opt.id;
                    return optValue == currentValue || optValue === currentValue;
                });
            }
            
            // Update child dropdown
            // For units/warehouses format, use 'value' and 'label' fields
            const valueField = (data.units || data.warehouses) ? 'value' : config.valueField;
            const labelField = (data.units || data.warehouses) ? 'label' : config.labelField;
            updateDropdownOptions(childElement, options, config.placeholder, valueField, labelField);
            
            // If current warehouse is not in allowed list but we have a current value, add it anyway
            // This preserves the selected warehouse even if it's not in the allowed list for the item
            // This is important for edit mode where warehouse was selected before item restrictions were applied
            if (isWarehouseDropdown && currentValue && !currentValueInList && currentOptionText) {
                console.log('[initCascadingDropdown] Current warehouse not in allowed list, adding it anyway:', currentValue, currentOptionText);
                const option = document.createElement('option');
                option.value = currentValue;
                option.textContent = currentOptionText;
                option.selected = true;
                childElement.appendChild(option);
            }
            
            // Handle default_unit for units API
            if (data.default_unit && data.units && data.units.length > 0) {
                const defaultOption = Array.from(childElement.options).find(opt => opt.value === data.default_unit);
                if (defaultOption && !childElement.value) {
                    childElement.value = data.default_unit;
                }
            }
            
            // Handle auto-select for sub_accounts API (if only one option)
            if (data.sub_accounts && data.sub_accounts.length === 1 && !childElement.value) {
                childElement.value = data.sub_accounts[0].id;
                childElement.dispatchEvent(new Event('change'));
            }
            
            // Handle auto-select for gl_accounts API (primary or first one)
            if (data.gl_accounts && data.gl_accounts.length > 0 && !childElement.value) {
                const primaryGL = data.gl_accounts.find(ga => ga.is_primary === 1);
                if (primaryGL) {
                    childElement.value = primaryGL.id;
                } else if (data.gl_accounts.length === 1) {
                    childElement.value = data.gl_accounts[0].id;
                }
            }
            
            // Restore current value if it exists (for warehouses)
            if (currentValue) {
                const matchingOption = Array.from(childElement.options).find(opt => opt.value == currentValue || opt.value === currentValue);
                if (matchingOption) {
                    childElement.value = matchingOption.value;
                }
            }
            
            // Enable dropdown
            childElement.disabled = false;
            
            // Trigger onChange callback
            if (config.onChange) {
                config.onChange(childElement.value, childElement);
            }
        })
        .catch(error => {
            console.error('Error fetching cascading options:', error);
            
            // Restore original HTML
            childElement.innerHTML = originalHTML;
            childElement.disabled = false;
            
            // Show error message
            if (config.onError) {
                config.onError(error, childElement);
            } else {
                alert('خطا در بارگذاری گزینه‌ها. لطفاً دوباره تلاش کنید.');
            }
        });
    });
    
    // Initial load if parent has value
    // BUT: Don't dispatch change event if child already has a value (edit mode)
    // This prevents disabling the dropdown when it already has a selected value
    // Check for value in multiple ways: childElement.value, selected option, or data-initial-value
    // Also check if dropdown already has options (populated by updateWarehouseChoices)
    const hasChildValue = childElement.value || 
                         childElement.querySelector('option[selected]') || 
                         childElement.hasAttribute('data-initial-value');
    const hasOptions = childElement.options.length > 1; // More than just placeholder
    
    if (parentElement.value && !hasChildValue && !hasOptions) {
        parentElement.dispatchEvent(new Event('change'));
    }
}

/**
 * Update dropdown options.
 * 
 * @param {HTMLElement} selectElement - Select element
 * @param {Array} options - Array of option objects
 * @param {string} placeholder - Placeholder option text
 * @param {string} valueField - Field name for option value (default: 'id')
 * @param {string} labelField - Field name for option label (default: 'name')
 */
function updateDropdownOptions(selectElement, options, placeholder = '--- Select ---', valueField = 'id', labelField = 'name') {
    // Clear existing options
    selectElement.innerHTML = '';
    
    // Add placeholder option
    const placeholderOption = document.createElement('option');
    placeholderOption.value = '';
    placeholderOption.textContent = placeholder;
    selectElement.appendChild(placeholderOption);
    
    // Add options from array
    options.forEach(option => {
        const optionElement = document.createElement('option');
        
        // Handle different option formats
        if (typeof option === 'string') {
            optionElement.value = option;
            optionElement.textContent = option;
        } else if (typeof option === 'object') {
            optionElement.value = option[valueField] || option.id || option.value || '';
            optionElement.textContent = option[labelField] || option.name || option.label || String(optionElement.value);
        } else {
            optionElement.value = String(option);
            optionElement.textContent = String(option);
        }
        
        selectElement.appendChild(optionElement);
    });
}

/**
 * Clear dropdown options.
 * 
 * @param {HTMLElement} selectElement - Select element
 * @param {string} placeholder - Placeholder option text
 */
function clearDropdown(selectElement, placeholder = '--- Select ---') {
    selectElement.innerHTML = '';
    const placeholderOption = document.createElement('option');
    placeholderOption.value = '';
    placeholderOption.textContent = placeholder;
    selectElement.appendChild(placeholderOption);
    selectElement.value = '';
}

/**
 * Initialize multiple cascading dropdowns from data attributes.
 * 
 * This function scans the page for elements with data-cascading attributes
 * and initializes them automatically.
 */
function initCascadingDropdowns() {
    const cascadingElements = document.querySelectorAll('[data-cascading-parent]');
    
    cascadingElements.forEach(childElement => {
        const parentSelector = childElement.dataset.cascadingParent;
        const apiUrl = childElement.dataset.cascadingApi;
        
        if (!parentSelector || !apiUrl) {
            console.warn('Missing data-cascading-parent or data-cascading-api attribute');
            return;
        }
        
        const parentElement = document.querySelector(parentSelector);
        if (!parentElement) {
            console.warn(`Parent element not found: ${parentSelector}`);
            return;
        }
        
        const options = {
            parentField: childElement.dataset.cascadingParentField || 'parent_id',
            placeholder: childElement.dataset.cascadingPlaceholder || '--- Select ---',
            valueField: childElement.dataset.cascadingValueField || 'id',
            labelField: childElement.dataset.cascadingLabelField || 'name',
        };
        
        initCascadingDropdown(parentElement, childElement, apiUrl, options);
    });
}

// Auto-initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCascadingDropdowns);
} else {
    initCascadingDropdowns();
}

