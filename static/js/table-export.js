/**
 * Table export utilities for exporting table data to CSV, Excel, and printing.
 * 
 * This file provides functions for exporting HTML table data to various formats.
 */

/**
 * Export table to CSV format.
 * 
 * @param {string} tableId - ID of the table element to export
 * @param {string} filename - Filename for the downloaded file (default: 'table.csv')
 * @param {Object} options - Configuration options
 * @param {boolean} options.includeHeaders - Include table headers (default: true)
 * @param {string} options.delimiter - CSV delimiter (default: ',')
 * @param {boolean} options.skipHiddenColumns - Skip hidden columns (default: true)
 */
function exportTableToCSV(tableId, filename = 'table.csv', options = {}) {
    const config = {
        includeHeaders: options.includeHeaders !== false,
        delimiter: options.delimiter || ',',
        skipHiddenColumns: options.skipHiddenColumns !== false,
    };
    
    const table = document.getElementById(tableId);
    if (!table) {
        console.error(`Table with ID "${tableId}" not found`);
        return;
    }
    
    // Extract table data
    const rows = [];
    const tableRows = table.querySelectorAll('tr');
    
    tableRows.forEach((row, rowIndex) => {
        // Skip header row if not including headers
        if (!config.includeHeaders && rowIndex === 0 && row.querySelector('th')) {
            return;
        }
        
        const cells = [];
        const cellElements = row.querySelectorAll('th, td');
        
        cellElements.forEach(cell => {
            // Skip hidden columns
            if (config.skipHiddenColumns) {
                const style = window.getComputedStyle(cell);
                if (style.display === 'none' || style.visibility === 'hidden') {
                    return;
                }
            }
            
            // Get cell text (strip HTML tags)
            let cellText = cell.textContent || cell.innerText || '';
            
            // Clean up whitespace
            cellText = cellText.trim().replace(/\s+/g, ' ');
            
            // Handle special characters in CSV
            // If contains delimiter, newline, or quote, wrap in quotes and escape quotes
            if (cellText.includes(config.delimiter) || 
                cellText.includes('\n') || 
                cellText.includes('"')) {
                cellText = '"' + cellText.replace(/"/g, '""') + '"';
            }
            
            cells.push(cellText);
        });
        
        if (cells.length > 0) {
            rows.push(cells.join(config.delimiter));
        }
    });
    
    // Create CSV content
    const csvContent = rows.join('\n');
    
    // Add BOM for UTF-8 to support Persian/Arabic characters in Excel
    const BOM = '\uFEFF';
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
    
    // Create download link
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Clean up
    URL.revokeObjectURL(url);
}

/**
 * Export table to Excel format.
 * 
 * Note: This function uses a simple CSV approach with .xlsx extension.
 * For full Excel support with formatting, consider using SheetJS library.
 * 
 * @param {string} tableId - ID of the table element to export
 * @param {string} filename - Filename for the downloaded file (default: 'table.xlsx')
 * @param {Object} options - Configuration options
 * @param {boolean} options.includeHeaders - Include table headers (default: true)
 * @param {boolean} options.skipHiddenColumns - Skip hidden columns (default: true)
 */
function exportTableToExcel(tableId, filename = 'table.xlsx', options = {}) {
    const config = {
        includeHeaders: options.includeHeaders !== false,
        skipHiddenColumns: options.skipHiddenColumns !== false,
    };
    
    // For now, use CSV format with .xlsx extension
    // Excel will open it correctly, but formatting will be basic
    // For advanced Excel features, integrate SheetJS library
    exportTableToCSV(tableId, filename, {
        ...config,
        delimiter: ',',
    });
    
    // TODO: For full Excel support, integrate SheetJS:
    // import * as XLSX from 'xlsx';
    // const wb = XLSX.utils.table_to_book(table);
    // XLSX.writeFile(wb, filename);
}

/**
 * Print table content.
 * 
 * @param {string} tableId - ID of the table element to print
 * @param {Object} options - Configuration options
 * @param {string} options.title - Print title (default: 'Table')
 * @param {boolean} options.includePageTitle - Include page title in print (default: true)
 * @param {boolean} options.includeDate - Include date in print (default: true)
 */
function printTable(tableId, options = {}) {
    const config = {
        title: options.title || 'Table',
        includePageTitle: options.includePageTitle !== false,
        includeDate: options.includeDate !== false,
    };
    
    const table = document.getElementById(tableId);
    if (!table) {
        console.error(`Table with ID "${tableId}" not found`);
        return;
    }
    
    // Clone table for printing
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
        alert('Please allow popups to print the table');
        return;
    }
    
    // Build HTML content
    let htmlContent = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>${config.title}</title>
    <style>
        @media print {
            @page {
                margin: 1cm;
            }
            body {
                margin: 0;
                padding: 0;
            }
        }
        body {
            font-family: Arial, sans-serif;
            direction: rtl;
            text-align: right;
        }
        .print-header {
            margin-bottom: 20px;
            border-bottom: 2px solid #000;
            padding-bottom: 10px;
        }
        .print-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .print-date {
            font-size: 12px;
            color: #666;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: right;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .no-print {
            display: none;
        }
    </style>
</head>
<body>
`;
    
    // Add header
    if (config.includePageTitle || config.includeDate) {
        htmlContent += '<div class="print-header">';
        if (config.includePageTitle) {
            htmlContent += `<div class="print-title">${config.title}</div>`;
        }
        if (config.includeDate) {
            const now = new Date();
            const dateStr = now.toLocaleDateString('fa-IR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
            });
            htmlContent += `<div class="print-date">${dateStr}</div>`;
        }
        htmlContent += '</div>';
    }
    
    // Clone table
    const clonedTable = table.cloneNode(true);
    
    // Remove hidden columns
    const hiddenElements = clonedTable.querySelectorAll('[style*="display: none"], [style*="visibility: hidden"], .no-print');
    hiddenElements.forEach(el => el.remove());
    
    // Remove action buttons and non-printable elements
    const actionButtons = clonedTable.querySelectorAll('button, .btn, .actions, .action-buttons');
    actionButtons.forEach(btn => {
        const cell = btn.closest('td, th');
        if (cell && cell.querySelectorAll('button, .btn, .actions, .action-buttons').length === 1) {
            cell.remove();
        } else {
            btn.remove();
        }
    });
    
    htmlContent += clonedTable.outerHTML;
    htmlContent += `
</body>
</html>
`;
    
    // Write content and print
    printWindow.document.write(htmlContent);
    printWindow.document.close();
    
    // Wait for content to load, then print
    printWindow.onload = function() {
        setTimeout(function() {
            printWindow.print();
            // Optionally close after printing
            // printWindow.close();
        }, 250);
    };
}

