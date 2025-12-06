/**
 * Item filtering utilities for inventory forms.
 * 
 * This file provides functions for managing item filtering in formsets:
 * - Filtering items by type, category, subcategory, and search
 * - Loading categories and subcategories dynamically
 * - Refreshing unit and warehouse options based on selected item
 */

/**
 * Filter items for a specific row based on type, category, subcategory, and search term.
 * 
 * @param {HTMLElement} rowElement - The row element containing filter inputs
 * @param {Object} options - Configuration options
 * @param {string} options.apiUrl - API endpoint URL (default: '/inventory/api/filtered-items/')
 * @param {string} options.typeSelector - Selector for type dropdown (default: '.filter-type-select')
 * @param {string} options.categorySelector - Selector for category dropdown (default: '.filter-category-select')
 * @param {string} options.subcategorySelector - Selector for subcategory dropdown (default: '.filter-subcategory-select')
 * @param {string} options.searchSelector - Selector for search input (default: '.filter-search-input')
 * @param {string} options.itemSelector - Selector for item dropdown (default: 'select[name*="-item"]')
 * @param {string} options.placeholder - Placeholder text for item dropdown (default: '--- Select ---')
 * @param {Function} options.onItemChange - Callback function when item changes
 */
function filterItemsForRow(rowElement, options = {}) {
  if (!rowElement) return;
  
  const config = {
    apiUrl: options.apiUrl || '/inventory/api/filtered-items/',
    typeSelector: options.typeSelector || '.filter-type-select',
    categorySelector: options.categorySelector || '.filter-category-select',
    subcategorySelector: options.subcategorySelector || '.filter-subcategory-select',
    searchSelector: options.searchSelector || '.filter-search-input',
    itemSelector: options.itemSelector || 'select[name*="-item"]',
    placeholder: options.placeholder || '--- Select ---',
    onItemChange: options.onItemChange || null,
  };
  
  const typeSelect = rowElement.querySelector(config.typeSelector);
  const categorySelect = rowElement.querySelector(config.categorySelector);
  const subcategorySelect = rowElement.querySelector(config.subcategorySelector);
  const searchInput = rowElement.querySelector(config.searchSelector);
  const itemSelect = rowElement.querySelector(config.itemSelector);
  
  if (!itemSelect) return;
  
  const typeId = typeSelect ? (typeSelect.value || '') : '';
  const categoryId = categorySelect ? (categorySelect.value || '') : '';
  const subcategoryId = subcategorySelect ? (subcategorySelect.value || '') : '';
  let searchTerm = searchInput ? (searchInput.value || '').trim() : '';
  
  if (searchTerm === 'None' || searchTerm === 'none' || searchTerm === 'null') {
    searchTerm = '';
  }
  
  let apiUrl = config.apiUrl;
  const params = new URLSearchParams();
  if (typeId) params.append('type_id', typeId);
  if (categoryId) params.append('category_id', categoryId);
  if (subcategoryId) params.append('subcategory_id', subcategoryId);
  if (searchTerm) params.append('search', searchTerm);
  
  if (params.toString()) {
    apiUrl += '?' + params.toString();
  }
  
  fetch(apiUrl)
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        console.error('[filterItemsForRow] API error:', data.error);
        return;
      }
      if (data.items) {
        const itemMap = {};
        data.items.forEach(function(item) {
          itemMap[item.value] = item;
        });
        
        const currentValue = itemSelect.value;
        
        itemSelect.innerHTML = '';
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = config.placeholder;
        itemSelect.appendChild(emptyOption);
        
        data.items.forEach(function(item) {
          const option = document.createElement('option');
          option.value = item.value;
          option.textContent = item.label;
          itemSelect.appendChild(option);
        });
        
        if (currentValue && itemMap[currentValue]) {
          itemSelect.value = currentValue;
          if (config.onItemChange) {
            config.onItemChange(itemSelect, rowElement);
          } else {
            itemSelect.dispatchEvent(new Event('change', { bubbles: true }));
          }
        } else if (currentValue) {
          itemSelect.value = '';
          // Clear dependent dropdowns
          const unitSelect = rowElement.querySelector('select[name*="-unit"]');
          const warehouseSelect = rowElement.querySelector('select[name*="-warehouse"]');
          if (unitSelect) {
            unitSelect.innerHTML = `<option value="">${config.placeholder}</option>`;
          }
          if (warehouseSelect) {
            warehouseSelect.innerHTML = `<option value="">${config.placeholder}</option>`;
          }
        }
      }
    })
    .catch(error => {
      console.error('[filterItemsForRow] Error:', error);
    });
}

/**
 * Load categories for a specific row based on selected type.
 * 
 * @param {HTMLElement} rowElement - The row element
 * @param {string|number} typeId - Selected type ID
 * @param {Object} options - Configuration options
 * @param {string} options.apiUrl - API endpoint URL (default: '/inventory/api/filtered-categories/')
 * @param {string} options.categorySelector - Selector for category dropdown
 * @param {string} options.subcategorySelector - Selector for subcategory dropdown
 * @param {string} options.allCategoriesText - Text for "All Categories" option
 * @param {string} options.allSubcategoriesText - Text for "All Subcategories" option
 */
function loadCategoriesForRow(rowElement, typeId, options = {}) {
  if (!rowElement) return;
  
  const config = {
    apiUrl: options.apiUrl || '/inventory/api/filtered-categories/',
    categorySelector: options.categorySelector || '.filter-category-select',
    subcategorySelector: options.subcategorySelector || '.filter-subcategory-select',
    allCategoriesText: options.allCategoriesText || 'All Categories',
    allSubcategoriesText: options.allSubcategoriesText || 'All Subcategories',
  };
  
  const categorySelect = rowElement.querySelector(config.categorySelector);
  const subcategorySelect = rowElement.querySelector(config.subcategorySelector);
  
  if (!categorySelect) return;
  
  categorySelect.innerHTML = `<option value="">${config.allCategoriesText}</option>`;
  if (subcategorySelect) {
    subcategorySelect.innerHTML = `<option value="">${config.allSubcategoriesText}</option>`;
  }
  
  const url = typeId ? `${config.apiUrl}?type_id=${typeId}` : config.apiUrl;
  
  fetch(url)
    .then(response => response.json())
    .then(data => {
      if (data.categories) {
        data.categories.forEach(function(cat) {
          const option = document.createElement('option');
          option.value = cat.value;
          option.textContent = cat.label;
          categorySelect.appendChild(option);
        });
      }
      // Re-filter items after categories are loaded
      filterItemsForRow(rowElement, options);
    })
    .catch(error => {
      console.error('[loadCategoriesForRow] Error:', error);
    });
}

/**
 * Load subcategories for a specific row based on selected category.
 * 
 * @param {HTMLElement} rowElement - The row element
 * @param {string|number} categoryId - Selected category ID
 * @param {Object} options - Configuration options
 * @param {string} options.apiUrl - API endpoint URL (default: '/inventory/api/filtered-subcategories/')
 * @param {string} options.subcategorySelector - Selector for subcategory dropdown
 * @param {string} options.allSubcategoriesText - Text for "All Subcategories" option
 */
function loadSubcategoriesForRow(rowElement, categoryId, options = {}) {
  if (!rowElement) return;
  
  const config = {
    apiUrl: options.apiUrl || '/inventory/api/filtered-subcategories/',
    subcategorySelector: options.subcategorySelector || '.filter-subcategory-select',
    allSubcategoriesText: options.allSubcategoriesText || 'All Subcategories',
  };
  
  const subcategorySelect = rowElement.querySelector(config.subcategorySelector);
  if (!subcategorySelect) return;
  
  subcategorySelect.innerHTML = `<option value="">${config.allSubcategoriesText}</option>`;
  
  if (!categoryId) {
    filterItemsForRow(rowElement, options);
    return;
  }
  
  fetch(`${config.apiUrl}?category_id=${categoryId}`)
    .then(response => response.json())
    .then(data => {
      if (data.subcategories) {
        data.subcategories.forEach(function(sub) {
          const option = document.createElement('option');
          option.value = sub.value;
          option.textContent = sub.label;
          subcategorySelect.appendChild(option);
        });
      }
      filterItemsForRow(rowElement, options);
    })
    .catch(error => {
      console.error('[loadSubcategoriesForRow] Error:', error);
    });
}

/**
 * Refresh unit options for a specific row based on selected item.
 * 
 * @param {HTMLElement} itemSelect - Item select element
 * @param {HTMLElement} unitSelect - Unit select element
 * @param {Object} options - Configuration options
 * @param {string} options.apiUrl - API endpoint URL (default: '/inventory/api/item-allowed-units/')
 * @param {string} options.placeholder - Placeholder text for unit dropdown
 */
function refreshLineUnitOptions(itemSelect, unitSelect, options = {}) {
  if (!itemSelect || !unitSelect) return;
  
  const config = {
    apiUrl: options.apiUrl || '/inventory/api/item-allowed-units/',
    placeholder: options.placeholder || '--- Select ---',
  };
  
  const selectedItem = itemSelect.value || '';
  
  if (selectedItem) {
    fetch(`${config.apiUrl}?item_id=${selectedItem}`)
      .then(response => response.json())
      .then(data => {
        if (data.units) {
          const currentValue = unitSelect.value;
          unitSelect.innerHTML = '';
          
          const placeholderOption = document.createElement('option');
          placeholderOption.value = '';
          placeholderOption.textContent = config.placeholder;
          unitSelect.appendChild(placeholderOption);
          
          data.units.forEach(function(option) {
            const optionEl = document.createElement('option');
            optionEl.value = option.value;
            optionEl.textContent = option.label;
            unitSelect.appendChild(optionEl);
          });
          
          if (currentValue && data.units.some(opt => opt.value === currentValue)) {
            unitSelect.value = currentValue;
          } else if (data.default_unit) {
            unitSelect.value = data.default_unit;
          }
        }
      })
      .catch(error => {
        console.error('[refreshLineUnitOptions] Error fetching units:', error);
      });
  } else {
    unitSelect.innerHTML = '';
    const placeholderOption = document.createElement('option');
    placeholderOption.value = '';
    placeholderOption.textContent = config.placeholder;
    unitSelect.appendChild(placeholderOption);
  }
}

/**
 * Refresh warehouse options for a specific row based on selected item.
 * 
 * @param {HTMLElement} itemSelect - Item select element
 * @param {HTMLElement} warehouseSelect - Warehouse select element
 * @param {Object} options - Configuration options
 * @param {string} options.apiUrl - API endpoint URL (default: '/inventory/api/item-allowed-warehouses/')
 * @param {string} options.placeholder - Placeholder text for warehouse dropdown
 */
function refreshLineWarehouseOptions(itemSelect, warehouseSelect, options = {}) {
  if (!itemSelect || !warehouseSelect) return;
  
  const config = {
    apiUrl: options.apiUrl || '/inventory/api/item-allowed-warehouses/',
    placeholder: options.placeholder || '--- Select ---',
  };
  
  const selectedItem = itemSelect.value || '';
  
  if (selectedItem) {
    fetch(`${config.apiUrl}?item_id=${selectedItem}`)
      .then(response => response.json())
      .then(data => {
        if (data.warehouses) {
          const currentValue = warehouseSelect.value;
          warehouseSelect.innerHTML = '';
          
          const placeholderOption = document.createElement('option');
          placeholderOption.value = '';
          placeholderOption.textContent = config.placeholder;
          warehouseSelect.appendChild(placeholderOption);
          
          data.warehouses.forEach(function(option) {
            const optionEl = document.createElement('option');
            optionEl.value = option.value;
            optionEl.textContent = option.label;
            warehouseSelect.appendChild(optionEl);
          });
          
          if (currentValue && data.warehouses.some(opt => opt.value === currentValue)) {
            warehouseSelect.value = currentValue;
          }
        }
      })
      .catch(error => {
        console.error('[refreshLineWarehouseOptions] Error fetching warehouses:', error);
      });
  } else {
    warehouseSelect.innerHTML = '';
    const placeholderOption = document.createElement('option');
    placeholderOption.value = '';
    placeholderOption.textContent = config.placeholder;
    warehouseSelect.appendChild(placeholderOption);
  }
}

/**
 * Initialize item filters for a formset row.
 * Sets up event listeners for type, category, subcategory, search, and item changes.
 * 
 * @param {HTMLElement} rowElement - The row element
 * @param {Object} options - Configuration options (passed to filter functions)
 */
function initializeItemFiltersForRow(rowElement, options = {}) {
  if (!rowElement) return;
  
  const typeSelect = rowElement.querySelector('.filter-type-select');
  const categorySelect = rowElement.querySelector('.filter-category-select');
  const subcategorySelect = rowElement.querySelector('.filter-subcategory-select');
  const searchInput = rowElement.querySelector('.filter-search-input');
  const itemSelect = rowElement.querySelector('select[name*="-item"]');
  const unitSelect = rowElement.querySelector('select[name*="-unit"]');
  const warehouseSelect = rowElement.querySelector('select[name*="-warehouse"]');
  
  // Type change handler
  if (typeSelect) {
    typeSelect.addEventListener('change', function() {
      loadCategoriesForRow(rowElement, this.value, options);
    });
  }
  
  // Category change handler
  if (categorySelect) {
    categorySelect.addEventListener('change', function() {
      loadSubcategoriesForRow(rowElement, this.value, options);
    });
  }
  
  // Subcategory change handler
  if (subcategorySelect) {
    subcategorySelect.addEventListener('change', function() {
      filterItemsForRow(rowElement, options);
    });
  }
  
  // Search input handler (with debounce)
  if (searchInput) {
    let searchTimeout;
    searchInput.addEventListener('input', function() {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(function() {
        filterItemsForRow(rowElement, options);
      }, 300);
    });
    
    searchInput.addEventListener('keyup', function(e) {
      if (e.key === 'Enter') {
        clearTimeout(searchTimeout);
        filterItemsForRow(rowElement, options);
      }
    });
  }
  
  // Item change handler - refresh unit and warehouse options
  if (itemSelect) {
    itemSelect.addEventListener('change', function() {
      const selectedItemId = this.value;
      
      if (selectedItemId) {
        if (unitSelect) {
          refreshLineUnitOptions(this, unitSelect, options);
        }
        if (warehouseSelect) {
          refreshLineWarehouseOptions(this, warehouseSelect, options);
        }
      } else {
        if (unitSelect) {
          unitSelect.innerHTML = `<option value="">${options.placeholder || '--- Select ---'}</option>`;
        }
        if (warehouseSelect) {
          warehouseSelect.innerHTML = `<option value="">${options.placeholder || '--- Select ---'}</option>`;
        }
      }
    });
    
    // Initial load if item already has value
    if (itemSelect.value) {
      if (unitSelect) refreshLineUnitOptions(itemSelect, unitSelect, options);
      if (warehouseSelect) refreshLineWarehouseOptions(itemSelect, warehouseSelect, options);
    }
    
    // Initial filter
    filterItemsForRow(rowElement, options);
  }
  
  // Initial category load if type has value
  if (typeSelect && typeSelect.value) {
    loadCategoriesForRow(rowElement, typeSelect.value, options);
  }
}

