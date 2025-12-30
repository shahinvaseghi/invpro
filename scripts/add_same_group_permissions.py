#!/usr/bin/env python
"""
Script to add SAME_GROUP permissions to all feature codes in FEATURE_PERMISSION_MAP.
"""
import re

def update_permissions_file(file_path):
    """Add SAME_GROUP permissions to all feature codes."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Add VIEW_SAME_GROUP after VIEW_ALL
    content = re.sub(
        r'(PermissionAction\.VIEW_ALL,\s*\n)',
        r'\1            PermissionAction.VIEW_SAME_GROUP,\n',
        content
    )
    
    # Add EDIT_SAME_GROUP after EDIT_OWN (but not if EDIT_OTHER follows)
    content = re.sub(
        r'(PermissionAction\.EDIT_OWN,\s*\n)(?!\s*PermissionAction\.EDIT_OTHER)',
        r'\1            PermissionAction.EDIT_SAME_GROUP,\n',
        content
    )
    
    # Add EDIT_SAME_GROUP after EDIT_OTHER
    content = re.sub(
        r'(PermissionAction\.EDIT_OTHER,\s*\n)',
        r'\1            PermissionAction.EDIT_SAME_GROUP,\n',
        content
    )
    
    # Add DELETE_SAME_GROUP after DELETE_OWN (but not if DELETE_OTHER follows)
    content = re.sub(
        r'(PermissionAction\.DELETE_OWN,\s*\n)(?!\s*PermissionAction\.DELETE_OTHER)',
        r'\1            PermissionAction.DELETE_SAME_GROUP,\n',
        content
    )
    
    # Add DELETE_SAME_GROUP after DELETE_OTHER
    content = re.sub(
        r'(PermissionAction\.DELETE_OTHER,\s*\n)',
        r'\1            PermissionAction.DELETE_SAME_GROUP,\n',
        content
    )
    
    # Add LOCK_SAME_GROUP after LOCK_OWN (but not if LOCK_OTHER follows)
    content = re.sub(
        r'(PermissionAction\.LOCK_OWN,\s*\n)(?!\s*PermissionAction\.LOCK_OTHER)',
        r'\1            PermissionAction.LOCK_SAME_GROUP,\n',
        content
    )
    
    # Add LOCK_SAME_GROUP after LOCK_OTHER
    content = re.sub(
        r'(PermissionAction\.LOCK_OTHER,\s*\n)',
        r'\1            PermissionAction.LOCK_SAME_GROUP,\n',
        content
    )
    
    # Add UNLOCK_SAME_GROUP after UNLOCK_OWN (but not if UNLOCK_OTHER follows)
    content = re.sub(
        r'(PermissionAction\.UNLOCK_OWN,\s*\n)(?!\s*PermissionAction\.UNLOCK_OTHER)',
        r'\1            PermissionAction.UNLOCK_SAME_GROUP,\n',
        content
    )
    
    # Add UNLOCK_SAME_GROUP after UNLOCK_OTHER
    content = re.sub(
        r'(PermissionAction\.UNLOCK_OTHER,\s*\n)',
        r'\1            PermissionAction.UNLOCK_SAME_GROUP,\n',
        content
    )
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {file_path}")
        return True
    else:
        print(f"⚠️  No changes needed in {file_path}")
        return False

if __name__ == '__main__':
    import sys
    file_path = 'shared/permissions.py'
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    update_permissions_file(file_path)




