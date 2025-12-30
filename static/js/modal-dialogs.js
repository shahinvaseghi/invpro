/**
 * Modal dialog utilities for displaying content in modal dialogs.
 * 
 * This file provides functions for creating and managing modal dialogs.
 */

/**
 * Show a simple modal dialog with content.
 * 
 * @param {string} title - Modal title
 * @param {string} content - Modal content (HTML or text)
 * @param {Object} options - Configuration options
 * @param {string} options.width - Modal width (default: '500px')
 * @param {string} options.height - Modal height (default: 'auto')
 * @param {boolean} options.closeOnOverlayClick - Close modal when clicking overlay (default: true)
 * @param {Function} options.onClose - Callback function called when modal is closed
 */
function showModal(title, content, options = {}) {
    const config = {
        width: options.width || '500px',
        height: options.height || 'auto',
        closeOnOverlayClick: options.closeOnOverlayClick !== false,
        onClose: options.onClose || null
    };
    
    // Remove existing modal if any
    const existingModal = document.getElementById('custom-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.id = 'custom-modal-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
    `;
    
    // Create modal container
    const modal = document.createElement('div');
    modal.id = 'custom-modal';
    modal.style.cssText = `
        background: white;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        width: ${config.width};
        max-width: 90vw;
        max-height: 90vh;
        overflow: auto;
        direction: rtl;
        text-align: right;
    `;
    
    // Create modal header
    const header = document.createElement('div');
    header.style.cssText = `
        padding: 1rem 1.5rem;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f9fafb;
    `;
    
    const titleElement = document.createElement('h3');
    titleElement.textContent = title;
    titleElement.style.cssText = `
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        color: #111827;
    `;
    
    const closeButton = document.createElement('button');
    closeButton.innerHTML = '×';
    closeButton.style.cssText = `
        background: none;
        border: none;
        font-size: 2rem;
        cursor: pointer;
        color: #6b7280;
        padding: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1;
    `;
    closeButton.onmouseover = function() {
        this.style.color = '#111827';
    };
    closeButton.onmouseout = function() {
        this.style.color = '#6b7280';
    };
    
    header.appendChild(titleElement);
    header.appendChild(closeButton);
    
    // Create modal body
    const body = document.createElement('div');
    body.style.cssText = `
        padding: 1.5rem;
        color: #374151;
        line-height: 1.6;
    `;
    body.innerHTML = content;
    
    // Create modal footer (optional)
    const footer = document.createElement('div');
    footer.style.cssText = `
        padding: 1rem 1.5rem;
        border-top: 1px solid #e5e7eb;
        display: flex;
        justify-content: flex-end;
        background: #f9fafb;
    `;
    
    const closeFooterButton = document.createElement('button');
    closeFooterButton.textContent = 'بستن';
    closeFooterButton.className = 'btn btn-secondary';
    closeFooterButton.style.cssText = `
        padding: 0.5rem 1rem;
        border: 1px solid #d1d5db;
        border-radius: 4px;
        background: #ffffff;
        color: #374151;
        cursor: pointer;
        font-size: 0.875rem;
    `;
    closeFooterButton.onmouseover = function() {
        this.style.backgroundColor = '#f3f4f6';
    };
    closeFooterButton.onmouseout = function() {
        this.style.backgroundColor = '#ffffff';
    };
    
    footer.appendChild(closeFooterButton);
    
    // Assemble modal
    modal.appendChild(header);
    modal.appendChild(body);
    modal.appendChild(footer);
    overlay.appendChild(modal);
    
    // Close function
    const closeModal = function() {
        overlay.remove();
        if (config.onClose) {
            config.onClose();
        }
    };
    
    // Event listeners
    closeButton.addEventListener('click', closeModal);
    closeFooterButton.addEventListener('click', closeModal);
    
    if (config.closeOnOverlayClick) {
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                closeModal();
            }
        });
    }
    
    // Close on Escape key
    const escapeHandler = function(e) {
        if (e.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', escapeHandler);
        }
    };
    document.addEventListener('keydown', escapeHandler);
    
    // Append to body
    document.body.appendChild(overlay);
    
    // Focus close button for accessibility
    closeButton.focus();
}

/**
 * Show notes in a modal dialog.
 * 
 * @param {string} notes - Notes content to display
 * @param {string} title - Modal title (default: 'Notes')
 * @param {Object} options - Configuration options (passed to showModal)
 */
function showNotes(notes, title = 'Notes', options = {}) {
    // Escape HTML to prevent XSS
    const escapedNotes = notes
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
        .replace(/\n/g, '<br>');
    
    showModal(title, escapedNotes, options);
}

/**
 * Show QC notes in a modal dialog.
 * 
 * @param {string} notes - QC notes content to display
 */
function showQCNotes(notes) {
    showNotes(notes, 'QC Notes');
}

/**
 * Show rejection notes in a modal dialog.
 * 
 * @param {string} notes - Rejection notes content to display
 */
function showRejectionNotes(notes) {
    showNotes(notes, 'Rejection Notes');
}

