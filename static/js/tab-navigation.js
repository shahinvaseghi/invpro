/**
 * Tab Navigation JavaScript
 * 
 * Handles tab switching functionality for pages with multiple tabs.
 * Usage:
 *   initTabNavigation('tab-button', 'tab-content', 'tab');
 */

(function() {
    'use strict';

    /**
     * Initialize tab navigation
     * @param {string} buttonSelector - CSS selector for tab buttons
     * @param {string} contentSelector - CSS selector for tab content
     * @param {string} urlParam - URL parameter name for active tab (default: 'tab')
     */
    function initTabNavigation(buttonSelector, contentSelector, urlParam) {
        urlParam = urlParam || 'tab';
        
        const buttons = document.querySelectorAll(buttonSelector);
        const contents = document.querySelectorAll(contentSelector);
        
        if (buttons.length === 0 || contents.length === 0) {
            console.warn('Tab navigation: No buttons or contents found');
            return;
        }
        
        // Get active tab from URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        const activeTab = urlParams.get(urlParam);
        
        // Set initial active tab
        if (activeTab) {
            switchTab(activeTab, buttons, contents, urlParam);
        } else {
            // Default to first tab that has active class, or first tab
            let defaultTab = null;
            buttons.forEach(function(button) {
                if (button.classList.contains('active')) {
                    defaultTab = button.dataset.tabName;
                }
            });
            if (!defaultTab && buttons.length > 0) {
                defaultTab = buttons[0].dataset.tabName;
            }
            if (defaultTab) {
                switchTab(defaultTab, buttons, contents, urlParam);
            }
        }
        
        // Add click handlers
        buttons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const tabName = this.dataset.tabName;
                if (tabName) {
                    switchTab(tabName, buttons, contents, urlParam);
                } else {
                    console.warn('Tab button missing data-tab-name attribute');
                }
            });
        });
    }
    
    /**
     * Switch to a specific tab
     * @param {string} tabName - Name of the tab to activate
     * @param {NodeList} buttons - All tab buttons
     * @param {NodeList} contents - All tab contents
     * @param {string} urlParam - URL parameter name
     */
    function switchTab(tabName, buttons, contents, urlParam) {
        if (!tabName) {
            console.warn('switchTab: tabName is required');
            return;
        }
        
        // Hide all tab contents
        contents.forEach(function(content) {
            content.classList.remove('active');
        });
        
        // Remove active class from all buttons
        buttons.forEach(function(button) {
            button.classList.remove('active');
        });
        
        // Show selected tab content
        const selectedContent = document.getElementById('tab-' + tabName);
        if (selectedContent) {
            selectedContent.classList.add('active');
        } else {
            console.warn('Tab content not found: #tab-' + tabName);
        }
        
        // Add active class to selected button
        buttons.forEach(function(button) {
            const buttonTabName = button.dataset.tabName;
            if (buttonTabName === tabName) {
                button.classList.add('active');
            }
        });
        
        // Update URL without reload
        const url = new URL(window.location);
        url.searchParams.set(urlParam, tabName);
        window.history.pushState({}, '', url);
    }
    
    // Export to global scope
    window.initTabNavigation = initTabNavigation;
    window.switchTab = switchTab;
})();

