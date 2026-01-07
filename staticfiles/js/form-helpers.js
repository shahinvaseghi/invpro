/**
 * Form helper utilities for common form operations.
 * 
 * This file provides functions for form validation, auto-submit, date pickers, and error display.
 */

/**
 * Initialize auto-submit for select element.
 * 
 * Automatically submits the form when the select value changes.
 * 
 * @param {string|HTMLElement} selectElement - Select element or selector
 * @param {Object} options - Configuration options
 * @param {boolean} options.validateBeforeSubmit - Validate form before submit (default: true)
 * @param {number} options.delay - Delay in milliseconds before submit (default: 0)
 */
function initAutoSubmit(selectElement, options = {}) {
    const config = {
        validateBeforeSubmit: options.validateBeforeSubmit !== false,
        delay: options.delay || 0,
    };
    
    const element = typeof selectElement === 'string' 
        ? document.querySelector(selectElement) 
        : selectElement;
    
    if (!element) {
        console.error('Select element not found');
        return;
    }
    
    const form = element.closest('form');
    if (!form) {
        console.error('Form element not found');
        return;
    }
    
    element.addEventListener('change', function() {
        const submitForm = () => {
            if (config.validateBeforeSubmit) {
                if (!validateForm(form)) {
                    return; // Don't submit if validation fails
                }
            }
            
            form.submit();
        };
        
        if (config.delay > 0) {
            setTimeout(submitForm, config.delay);
        } else {
            submitForm();
        }
    });
}

/**
 * Initialize date picker for input element.
 * 
 * This is a wrapper function. You need to integrate with your preferred date picker library
 * (e.g., Persian Date Picker, Flatpickr, etc.)
 * 
 * @param {string|HTMLElement} inputElement - Input element or selector
 * @param {Object} options - Configuration options
 * @param {string} options.locale - Locale ('fa' for Persian, 'en' for English, default: 'fa')
 * @param {string} options.format - Date format (default: 'YYYY-MM-DD' for Persian, 'MM/DD/YYYY' for English)
 * @param {boolean} options.timePicker - Enable time picker (default: false)
 * @param {string} options.minDate - Minimum selectable date
 * @param {string} options.maxDate - Maximum selectable date
 */
function initDatePicker(inputElement, options = {}) {
    const config = {
        locale: options.locale || 'fa',
        format: options.format || null,
        timePicker: options.timePicker || false,
        minDate: options.minDate || null,
        maxDate: options.maxDate || null,
    };
    
    const element = typeof inputElement === 'string' 
        ? document.querySelector(inputElement) 
        : inputElement;
    
    if (!element) {
        console.error('Input element not found');
        return;
    }
    
    // Set default format based on locale
    if (!config.format) {
        config.format = config.locale === 'fa' ? 'YYYY-MM-DD' : 'MM/DD/YYYY';
    }
    
    // Check if a date picker library is available
    // This is a placeholder - integrate with your preferred library
    
    // Example integration points:
    // - If using Persian Date Picker (pwt-datepicker):
    //   $(element).pwtdatepicker({ format: config.format, ... });
    
    // - If using Flatpickr:
    //   flatpickr(element, { locale: config.locale, dateFormat: config.format, ... });
    
    // - If using native HTML5 date picker:
    if (element.type === 'date') {
        // Native date picker is already initialized
        if (config.minDate) {
            element.setAttribute('min', config.minDate);
        }
        if (config.maxDate) {
            element.setAttribute('max', config.maxDate);
        }
        return;
    }
    
    // Fallback: log warning if no date picker library detected
    console.warn('Date picker library not detected. Please integrate with your preferred date picker library.');
    console.info('Available options:', config);
}

/**
 * Validate form before submission.
 * 
 * @param {string|HTMLElement} formElement - Form element or selector
 * @param {Object} options - Configuration options
 * @param {boolean} options.showErrors - Show error messages (default: true)
 * @param {boolean} options.focusFirstError - Focus first error field (default: true)
 * @returns {boolean} - True if form is valid, false otherwise
 */
function validateForm(formElement, options = {}) {
    const config = {
        showErrors: options.showErrors !== false,
        focusFirstError: options.focusFirstError !== false,
    };
    
    const form = typeof formElement === 'string' 
        ? document.querySelector(formElement) 
        : formElement;
    
    if (!form) {
        console.error('Form element not found');
        return false;
    }
    
    // Clear previous errors
    if (config.showErrors) {
        clearFormErrors(form);
    }
    
    // Use HTML5 validation
    if (!form.checkValidity()) {
        // Get first invalid field
        const firstInvalid = form.querySelector(':invalid');
        
        if (config.focusFirstError && firstInvalid) {
            firstInvalid.focus();
            firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        
        if (config.showErrors) {
            // Show browser's default validation messages
            form.reportValidity();
        }
        
        return false;
    }
    
    // Additional custom validation can be added here
    // Check for custom validation attributes or data attributes
    
    return true;
}

/**
 * Display form errors.
 * 
 * @param {string|HTMLElement} formElement - Form element or selector
 * @param {Object} errors - Error object with field names as keys and error messages as values
 * @param {Object} options - Configuration options
 * @param {string} options.errorClass - CSS class for error messages (default: 'error-message')
 * @param {string} options.fieldErrorClass - CSS class for fields with errors (default: 'is-invalid')
 */
function showFormErrors(formElement, errors, options = {}) {
    const config = {
        errorClass: options.errorClass || 'error-message',
        fieldErrorClass: options.fieldErrorClass || 'is-invalid',
    };
    
    const form = typeof formElement === 'string' 
        ? document.querySelector(formElement) 
        : formElement;
    
    if (!form) {
        console.error('Form element not found');
        return;
    }
    
    // Clear previous errors first
    clearFormErrors(form);
    
    if (!errors || typeof errors !== 'object') {
        return;
    }
    
    // Display errors for each field
    Object.keys(errors).forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (!field) {
            console.warn(`Field "${fieldName}" not found in form`);
            return;
        }
        
        const errorMessage = errors[fieldName];
        if (!errorMessage) {
            return;
        }
        
        // Add error class to field
        field.classList.add(config.fieldErrorClass);
        
        // Create or find error message element
        let errorElement = field.parentElement.querySelector(`.${config.errorClass}`);
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = config.errorClass;
            errorElement.setAttribute('role', 'alert');
            
            // Insert after field or its label
            const label = form.querySelector(`label[for="${field.id}"]`);
            if (label && label.nextSibling) {
                label.parentNode.insertBefore(errorElement, label.nextSibling);
            } else if (field.parentElement) {
                field.parentElement.appendChild(errorElement);
            }
        }
        
        errorElement.textContent = errorMessage;
        errorElement.style.display = 'block';
    });
    
    // Display non-field errors (form-level errors)
    if (errors.__all__ || errors.non_field_errors) {
        const formErrors = errors.__all__ || errors.non_field_errors;
        const formErrorContainer = form.querySelector('.form-errors') || 
                                  form.querySelector('.alert-danger');
        
        if (formErrorContainer) {
            formErrorContainer.textContent = Array.isArray(formErrors) 
                ? formErrors.join(' ') 
                : formErrors;
            formErrorContainer.style.display = 'block';
        } else {
            // Create form error container
            const errorContainer = document.createElement('div');
            errorContainer.className = 'alert alert-danger form-errors';
            errorContainer.setAttribute('role', 'alert');
            errorContainer.textContent = Array.isArray(formErrors) 
                ? formErrors.join(' ') 
                : formErrors;
            
            form.insertBefore(errorContainer, form.firstChild);
        }
    }
}

/**
 * Clear all form errors.
 * 
 * @param {string|HTMLElement} formElement - Form element or selector
 * @param {Object} options - Configuration options
 * @param {string} options.errorClass - CSS class for error messages (default: 'error-message')
 * @param {string} options.fieldErrorClass - CSS class for fields with errors (default: 'is-invalid')
 */
function clearFormErrors(formElement, options = {}) {
    const config = {
        errorClass: options.errorClass || 'error-message',
        fieldErrorClass: options.fieldErrorClass || 'is-invalid',
    };
    
    const form = typeof formElement === 'string' 
        ? document.querySelector(formElement) 
        : formElement;
    
    if (!form) {
        return;
    }
    
    // Remove error class from all fields
    const errorFields = form.querySelectorAll(`.${config.fieldErrorClass}`);
    errorFields.forEach(field => {
        field.classList.remove(config.fieldErrorClass);
    });
    
    // Hide or remove error message elements
    const errorMessages = form.querySelectorAll(`.${config.errorClass}`);
    errorMessages.forEach(msg => {
        msg.style.display = 'none';
        msg.textContent = '';
    });
    
    // Clear form-level errors
    const formErrors = form.querySelectorAll('.form-errors, .alert-danger');
    formErrors.forEach(err => {
        err.style.display = 'none';
        err.textContent = '';
    });
}

