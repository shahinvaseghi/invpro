"""
Views for inventory module.

This file is kept for backward compatibility.
All views have been refactored into inventory.views package.

For new code, use:
    from inventory.views import ViewName
    from inventory.views.master_data import ItemListView
    from inventory.views.receipts import ReceiptPermanentListView
    etc.
"""
# Import everything from the package for backward compatibility
from inventory.views import *  # noqa: F401, F403
