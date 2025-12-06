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
            } else {
                console.warn('Unexpected API response format:', data);
                options = [];
            }
            
            // Update child dropdown
            // For units/warehouses format, use 'value' and 'label' fields
            const valueField = (data.units || data.warehouses) ? 'value' : config.valueField;
            const labelField = (data.units || data.warehouses) ? 'label' : config.labelField;
            updateDropdownOptions(childElement, options, config.placeholder, valueField, labelField);
            
            // Handle default_unit for units API
            if (data.default_unit && data.units && data.units.length > 0) {
                const defaultOption = Array.from(childElement.options).find(opt => opt.value === data.default_unit);
                if (defaultOption && !childElement.value) {
                    childElement.value = data.default_unit;
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
    if (parentElement.value) {
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

