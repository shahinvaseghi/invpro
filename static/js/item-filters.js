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
  // #region agent log
  fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:24',message:'filterItemsForRow called',data:{hasRowElement:!!rowElement,options},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'T'})}).catch(()=>{});
  // #endregion
  
  if (!rowElement) {
    // #region agent log
    fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:27',message:'filterItemsForRow: rowElement is null',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'T'})}).catch(()=>{});
    // #endregion
    return;
  }
  
  // Prevent repopulation if item is already selected and we're not filtering
  // This prevents the dropdown from clearing when user selects an item
  const skipRepopulate = options.skipRepopulate === true; // Only skip if explicitly set to true
  
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
  
  // Find item select - must match exactly "name*='-item'" but NOT "name*='-item_type_filter'" etc.
  let itemSelect = null;
  const allSelects = rowElement.querySelectorAll('select');
  for (let select of allSelects) {
    if (select.name && select.name.includes('-item') && !select.name.includes('_filter')) {
      itemSelect = select;
      break;
    }
  }
  
  // Fallback: try alternative selectors
  if (!itemSelect) {
    itemSelect = rowElement.querySelector('select.item-select:not([name*="_filter"])');
    if (!itemSelect) {
      const wrapperSelects = rowElement.querySelectorAll('.item-select-wrapper select');
      for (let select of wrapperSelects) {
        if (select.name && select.name.includes('-item') && !select.name.includes('_filter')) {
          itemSelect = select;
          break;
        }
      }
    }
  }
  
  // #region agent log
  fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:48',message:'filterItemsForRow: elements found',data:{hasTypeSelect:!!typeSelect,hasCategorySelect:!!categorySelect,hasSubcategorySelect:!!subcategorySelect,hasSearchInput:!!searchInput,hasItemSelect:!!itemSelect,itemSelectName:itemSelect?.name,itemSelector:config.itemSelector},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'T'})}).catch(()=>{});
  // #endregion
  
  if (!itemSelect) {
    // #region agent log
    fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:51',message:'filterItemsForRow: itemSelect not found',data:{itemSelector:config.itemSelector,rowElementHTML:rowElement.innerHTML.substring(0,200)},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'T'})}).catch(()=>{});
    // #endregion
    return;
  }
  
  const typeId = typeSelect ? (typeSelect.value || '') : '';
  const categoryId = categorySelect ? (categorySelect.value || '') : '';
  const subcategoryId = subcategorySelect ? (subcategorySelect.value || '') : '';
  let searchTerm = searchInput ? (searchInput.value || '').trim() : '';
  
  if (searchTerm === 'None' || searchTerm === 'none' || searchTerm === 'null') {
    searchTerm = '';
  }
  
  // Check if dropdown is already populated - if so, don't repopulate unless filters changed
  const isAlreadyPopulated = itemSelect && itemSelect.getAttribute('data-populated') === 'true';
  const hasOptions = itemSelect && itemSelect.querySelectorAll('option').length > 1; // More than just placeholder
  
  // If dropdown is already populated and no filters are active, don't repopulate
  // This prevents clearing the selection when user selects an item or when reinitializing
  if (isAlreadyPopulated && hasOptions && !typeId && !categoryId && !subcategoryId && !searchTerm && skipRepopulate) {
    console.log('[item-filters] Skipping repopulation - dropdown already populated and no filters', {
      isAlreadyPopulated,
      hasOptions,
      currentValue: itemSelect ? itemSelect.value : null
    });
    // #region agent log
    fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:95',message:'Skipping repopulation - dropdown already populated and no filters',data:{isAlreadyPopulated,hasOptions,currentValue:itemSelect.value},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'N'})}).catch(()=>{});
    // #endregion
    return;
  }
  
  // Parse API URL to extract base URL and existing params
  let apiUrl = config.apiUrl;
  const urlParts = apiUrl.split('?');
  const baseUrl = urlParts[0];
  const existingParams = new URLSearchParams(urlParts[1] || '');
  
  // Build params object
  const params = new URLSearchParams();
  
  // Preserve existing params from apiUrl (like sellable_only) - IMPORTANT!
  for (const [key, value] of existingParams.entries()) {
    params.append(key, value);
  }
  
  // Ensure sellable_only is set if it was in the original URL
  if (existingParams.has('sellable_only') && !params.has('sellable_only')) {
    params.append('sellable_only', existingParams.get('sellable_only'));
  }
  
  // Add filter params
  if (typeId) params.append('type_id', typeId);
  if (categoryId) params.append('category_id', categoryId);
  if (subcategoryId) params.append('subcategory_id', subcategoryId);
  if (searchTerm) params.append('search', searchTerm);
  
  // Build final URL
  if (params.toString()) {
    apiUrl = baseUrl + '?' + params.toString();
  } else {
    apiUrl = baseUrl;
  }
  
  // Debug: Log the final URL to ensure sellable_only is included
  console.log('[item-filters] Final API URL', {
    apiUrl,
    hasSellableOnly: apiUrl.includes('sellable_only=true'),
    allParams: Array.from(params.entries())
  });
  
  // #region agent log
  console.log('[item-filters] Before API fetch', {
    apiUrl,
    hasItemSelect: !!itemSelect,
    itemSelectName: itemSelect?.name,
    sellableOnly: existingParams.get('sellable_only')
  });
  fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:82',message:'Before API fetch',data:{apiUrl,hasItemSelect:!!itemSelect,itemSelectName:itemSelect?.name,sellableOnly:existingParams.get('sellable_only')},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'R'})}).catch(()=>{});
  // #endregion
  
  fetch(apiUrl)
    .then(response => {
      // #region agent log
      console.log('[item-filters] API response received', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        url: apiUrl
      });
      fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:88',message:'API response received',data:{status:response.status,statusText:response.statusText,ok:response.ok,url:apiUrl},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'R'})}).catch(()=>{});
      // #endregion
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // #region agent log
      console.log('[item-filters] API data parsed', {
        hasError: !!data.error,
        error: data.error,
        hasItems: !!data.items,
        itemsCount: data.items?.length || 0,
        items: data.items?.slice(0, 5) || [] // First 5 items for debugging
      });
      fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:94',message:'API data parsed',data:{hasError:!!data.error,error:data.error,hasItems:!!data.items,itemsCount:data.items?.length || 0,firstItems:data.items?.slice(0,5)},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'R'})}).catch(()=>{});
      // #endregion
      
      if (data.error) {
        console.error('[filterItemsForRow] API error:', data.error);
        // #region agent log
        fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:99',message:'API returned error',data:{error:data.error},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'R'})}).catch(()=>{});
        // #endregion
        return;
      }
      if (data.items) {
        console.log('[item-filters] Populating dropdown with items', {
          itemsCount: data.items.length,
          itemSelectName: itemSelect.name,
          firstItems: data.items.slice(0, 5).map(i => ({ value: i.value, label: i.label }))
        });
        
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
        
        console.log('[item-filters] Dropdown populated', {
          optionsCount: itemSelect.querySelectorAll('option').length,
          currentValue: currentValue
        });
        
        // Mark as populated and show the dropdown
        itemSelect.setAttribute('data-populated', 'true');
        itemSelect.style.display = 'block';
        itemSelect.style.width = '100%';
        itemSelect.style.marginTop = '0.5rem';
        itemSelect.style.visibility = 'visible';
        itemSelect.style.opacity = '1';
        
        // #region agent log
        const computedStyle = window.getComputedStyle(itemSelect);
        fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:118',message:'Dropdown populated and shown',data:{itemsCount:data.items.length,dataPopulated:itemSelect.getAttribute('data-populated'),display:itemSelect.style.display,computedDisplay:computedStyle.display,visibility:computedStyle.visibility,opacity:computedStyle.opacity,optionsCount:itemSelect.querySelectorAll('option').length},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'P'})}).catch(()=>{});
        // #endregion
        
        // Force reflow to ensure display change takes effect
        itemSelect.offsetHeight;
        
        // Restore previous selection if it exists in the new list
        if (currentValue && itemMap[currentValue]) {
          itemSelect.value = currentValue;
          // Don't trigger change event to prevent repopulation
          // The change event will be triggered by user interaction, not programmatically
        } else if (currentValue) {
          // Current value is not in filtered list, clear it
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
        
        // Trigger change event only if onItemChange callback is provided
        // This prevents automatic repopulation when user selects an item
        if (config.onItemChange && currentValue && itemMap[currentValue]) {
          config.onItemChange(itemSelect, rowElement);
        }
      }
    })
    .catch(error => {
      console.error('[filterItemsForRow] Error:', error);
      // #region agent log
      fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:155',message:'API fetch failed',data:{error:error.message,errorStack:error.stack,apiUrl},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'S'})}).catch(()=>{});
      // #endregion
      
      // Show dropdown even if API fails - add empty option
      if (itemSelect) {
        itemSelect.innerHTML = '';
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = config.placeholder;
        itemSelect.appendChild(emptyOption);
        itemSelect.setAttribute('data-populated', 'true');
        itemSelect.style.display = 'block';
        itemSelect.style.width = '100%';
        itemSelect.style.marginTop = '0.5rem';
      }
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
  // #region agent log
  fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:424',message:'initializeItemFiltersForRow called',data:{hasRowElement:!!rowElement,options},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'I'})}).catch(()=>{});
  // #endregion
  
  if (!rowElement) {
    // #region agent log
    fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:427',message:'initializeItemFiltersForRow: rowElement is null',data:{},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'I'})}).catch(()=>{});
    // #endregion
    return;
  }
  
  const config = {
    typeSelector: options.typeSelector || '.filter-type-select',
    categorySelector: options.categorySelector || '.filter-category-select',
    subcategorySelector: options.subcategorySelector || '.filter-subcategory-select',
    searchSelector: options.searchSelector || '.filter-search-input',
    itemSelector: options.itemSelector || 'select[name*="-item"]',
  };
  
  // #region agent log
  fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:433',message:'initializeItemFiltersForRow: config created',data:{config},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'I'})}).catch(()=>{});
  // #endregion
  
  const typeSelect = rowElement.querySelector(config.typeSelector);
  const categorySelect = rowElement.querySelector(config.categorySelector);
  const subcategorySelect = rowElement.querySelector(config.subcategorySelector);
  const searchInput = rowElement.querySelector(config.searchSelector);
  
  // Find item select - must match exactly "name*='-item'" but NOT "name*='-item_type_filter'" etc.
  // Use more specific selector: select with name ending in "-item" but not containing "_filter"
  let itemSelect = null;
  const rowSelects = rowElement.querySelectorAll('select');
  for (let select of rowSelects) {
    if (select.name && select.name.includes('-item') && !select.name.includes('_filter')) {
      itemSelect = select;
      break;
    }
  }
  
  // Fallback: try alternative selectors
  if (!itemSelect) {
    itemSelect = rowElement.querySelector('select.item-select:not([name*="_filter"])');
    if (!itemSelect) {
      const wrapperSelects = rowElement.querySelectorAll('.item-select-wrapper select');
      for (let select of wrapperSelects) {
        if (select.name && select.name.includes('-item') && !select.name.includes('_filter')) {
          itemSelect = select;
          break;
        }
      }
    }
  }
  
  const unitSelect = rowElement.querySelector('select[name*="-unit"]');
  const warehouseSelect = rowElement.querySelector('select[name*="-warehouse"]');
  
  // Debug: Log all selects found in row (reuse rowSelects from above)
  // #region agent log
  const allSelectNames = Array.from(rowSelects).map(s => ({ name: s.name, id: s.id, className: s.className }));
  console.log('[item-filters] All selects in row:', allSelectNames);
  console.log('[item-filters] Looking for item select with selector:', config.itemSelector);
  console.log('[item-filters] Item select found:', !!itemSelect, itemSelect ? { name: itemSelect.name, id: itemSelect.id, className: itemSelect.className } : 'not found');
  fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:441',message:'All selects found in row',data:{allSelectNames,itemSelector:config.itemSelector,hasItemSelect:!!itemSelect,itemSelectName:itemSelect?.name,itemSelectId:itemSelect?.id,itemSelectClassName:itemSelect?.className},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'D'})}).catch(()=>{});
  // #endregion
  
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
  // IMPORTANT: Don't trigger filterItemsForRow on item change to prevent repopulation
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
    }, { once: false }); // Keep listener active but don't trigger filterItemsForRow
    
    // Initial load if item already has value
    if (itemSelect.value) {
      if (unitSelect) refreshLineUnitOptions(itemSelect, unitSelect, options);
      if (warehouseSelect) refreshLineWarehouseOptions(itemSelect, warehouseSelect, options);
    }
  }
  
  // Initial filter - always call to populate dropdown with all available items
  // This ensures the dropdown is populated even if no filters are set
  // #region agent log
  const rowHTML = rowElement ? rowElement.innerHTML.substring(0, 300) : 'no rowElement';
  const itemSelectInfo = itemSelect ? {
    name: itemSelect.name,
    id: itemSelect.id,
    className: itemSelect.className,
    display: itemSelect.style.display,
    dataPopulated: itemSelect.getAttribute('data-populated'),
    optionsCount: itemSelect.querySelectorAll('option').length,
    parentElement: itemSelect.parentElement ? itemSelect.parentElement.className : 'no parent'
  } : 'no itemSelect';
  fetch('http://localhost:7242/ingest/722004b4-76f8-4beb-97ce-3ab1b68e1cbc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'item-filters.js:510',message:'About to call initial filterItemsForRow',data:{hasItemSelect:!!itemSelect,itemSelectInfo,hasRowElement:!!rowElement,rowHTML,config:config},timestamp:Date.now(),sessionId:'debug-session',runId:'run5',hypothesisId:'Q'})}).catch(()=>{});
  // #endregion
  
  // Always call filterItemsForRow to populate dropdown for each row
  // Only skip repopulation if dropdown is already populated AND has options (to avoid clearing it)
  // But always populate on initial load (when data-populated is not set)
  if (itemSelect) {
    const isAlreadyPopulated = itemSelect.getAttribute('data-populated') === 'true';
    const optionsCount = itemSelect.querySelectorAll('option').length;
    const hasOptions = optionsCount > 1; // More than just placeholder
    
    // Only skip if BOTH conditions are true: already populated AND has options
    // This ensures initial population always happens for empty dropdowns
    const shouldSkipRepopulate = isAlreadyPopulated && hasOptions;
    
    console.log('[item-filters] Calling filterItemsForRow for row', {
      hasItemSelect: !!itemSelect,
      itemSelectName: itemSelect.name,
      itemSelectId: itemSelect.id,
      rowElement: !!rowElement,
      isAlreadyPopulated,
      hasOptions,
      optionsCount,
      shouldSkipRepopulate
    });
    
    // Always call filterItemsForRow - it will check skipRepopulate internally
    // For initial load, skipRepopulate should be false to ensure dropdown is populated
    const filterOptions = Object.assign({}, options, { skipRepopulate: shouldSkipRepopulate });
    filterItemsForRow(rowElement, filterOptions);
  } else {
    console.error('[item-filters] Cannot call filterItemsForRow - itemSelect not found in row', {
      itemSelector: config.itemSelector,
      rowElement: !!rowElement,
      allSelects: Array.from(rowElement.querySelectorAll('select')).map(function(s) {
        return {
          name: s.name,
          id: s.id,
          className: s.className
        };
      })
    });
  }
  
  // Initial category load if type has value
  if (typeSelect && typeSelect.value) {
    loadCategoriesForRow(rowElement, typeSelect.value, options);
  }
}

