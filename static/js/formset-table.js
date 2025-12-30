/**
 * Formset table layout utilities.
 * 
 * This file provides functions for managing grid layout in formset tables,
 * including dynamic column configuration based on can_delete attribute.
 */

/**
 * Initialize formset table grid layout.
 * Sets up grid-template-columns based on can_delete attribute and column configuration.
 * 
 * @param {string|HTMLElement} container - Formset container element or selector
 * @param {Object} options - Configuration options
 * @param {string} options.columnsWithDelete - Grid template columns when delete is enabled
 * @param {string} options.columnsWithoutDelete - Grid template columns when delete is disabled
 * @param {string} options.canDeleteAttribute - Attribute name for can_delete (default: 'data-can-delete')
 * @param {string} options.headerSelector - Selector for header element (default: '.formset-table-header, .lines-table-header')
 * @param {string} options.rowSelector - Selector for row elements (default: '.formset-table-row, .line-row')
 */
function initFormsetTableLayout(container, options = {}) {
  const containerElement = typeof container === 'string' 
    ? document.querySelector(container) 
    : container;
  
  if (!containerElement) {
    console.error('Formset table container not found');
    return;
  }
  
  const config = {
    columnsWithDelete: options.columnsWithDelete || '50px 3fr 1.5fr 1.5fr 2fr 2fr 80px',
    columnsWithoutDelete: options.columnsWithoutDelete || '50px 3fr 1.5fr 1.5fr 2fr 2fr',
    canDeleteAttribute: options.canDeleteAttribute || 'data-can-delete',
    headerSelector: options.headerSelector || '.formset-table-header, .lines-table-header',
    rowSelector: options.rowSelector || '.formset-table-row, .line-row',
  };
  
  // Get can_delete attribute
  const canDelete = containerElement.getAttribute(config.canDeleteAttribute) === 'true';
  const gridColumns = canDelete ? config.columnsWithDelete : config.columnsWithoutDelete;
  
  // Apply to header
  const header = containerElement.querySelector(config.headerSelector);
  if (header) {
    header.style.gridTemplateColumns = gridColumns;
  }
  
  // Apply to all rows
  const rows = containerElement.querySelectorAll(config.rowSelector);
  rows.forEach(function(row) {
    row.style.gridTemplateColumns = gridColumns;
  });
  
  return {
    canDelete,
    gridColumns,
    container: containerElement,
  };
}

/**
 * Update formset table layout after adding/removing rows.
 * Re-applies grid layout to all rows.
 * 
 * @param {string|HTMLElement} container - Formset container element or selector
 * @param {Object} options - Configuration options (same as initFormsetTableLayout)
 */
function updateFormsetTableLayout(container, options = {}) {
  return initFormsetTableLayout(container, options);
}

/**
 * Auto-initialize formset table layouts on page load.
 * Looks for elements with class 'formset-table' or 'lines-formset'.
 */
function initAllFormsetTables() {
  const containers = document.querySelectorAll('.formset-table, .lines-formset');
  containers.forEach(function(container) {
    // Try to detect column configuration from existing rows
    const firstRow = container.querySelector('.formset-table-row, .line-row');
    if (firstRow && firstRow.style.gridTemplateColumns) {
      // Use existing configuration
      const gridColumns = firstRow.style.gridTemplateColumns;
      const canDelete = container.getAttribute('data-can-delete') === 'true';
      
      initFormsetTableLayout(container, {
        columnsWithDelete: gridColumns,
        columnsWithoutDelete: gridColumns,
      });
    } else {
      // Use default configuration
      initFormsetTableLayout(container);
    }
  });
}

// Auto-initialize on DOM ready
// Note: This is disabled by default to allow templates to control initialization
// Uncomment the lines below if you want auto-initialization for all formsets
/*
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAllFormsetTables);
} else {
  initAllFormsetTables();
}
*/

