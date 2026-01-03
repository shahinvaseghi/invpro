"""
Template tags for rendering menus from centralized menu configuration.
"""
from django import template
from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext as _

from ui.menu_config import get_menu_structure, MenuItem, MenuSection

register = template.Library()


def check_permission(user, user_feature_permissions, item: MenuItem) -> bool:
    """
    Check if user has permission to see a menu item.
    
    Args:
        user: Django user object
        user_feature_permissions: Dictionary of user permissions
        item: MenuItem to check
        
    Returns:
        bool: True if user can see the item
    """
    # Check superuser requirement
    if item.requires_superuser and not user.is_superuser:
        return False
    
    # Check staff requirement
    if item.requires_staff and not (user.is_staff or user.is_superuser):
        return False
    
    # Check permission
    if item.permission:
        # Import here to avoid circular imports
        from shared.templatetags.access_tags import feature_allowed
        # Create a mock filter function
        class MockFilter:
            def feature_allowed(self, permission):
                return user_feature_permissions.get(permission, False)
        
        mock_filter = MockFilter()
        if not mock_filter.feature_allowed(item.permission):
            return False
    
    return True


def filter_menu_items(user, user_feature_permissions, items: list) -> list:
    """
    Filter menu items based on user permissions.
    
    Args:
        user: Django user object
        user_feature_permissions: Dictionary of user permissions
        items: List of MenuItem objects
        
    Returns:
        list: Filtered list of MenuItem objects
    """
    filtered_items = []
    
    for item in items:
        if not check_permission(user, user_feature_permissions, item):
            continue
        
        # Recursively filter children
        if item.children:
            filtered_children = filter_menu_items(user, user_feature_permissions, item.children)
            if filtered_children:
                # Create a copy of item with filtered children
                filtered_item = MenuItem(
                    name=item.name,
                    url_name=item.url_name,
                    icon=item.icon,
                    permission=item.permission,
                    requires_superuser=item.requires_superuser,
                    requires_staff=item.requires_staff,
                    target=item.target,
                    children=filtered_children
                )
                filtered_items.append(filtered_item)
        else:
            filtered_items.append(item)
    
    return filtered_items


def filter_menu_sections(user, user_feature_permissions, sections: list) -> list:
    """
    Filter menu sections based on user permissions.
    
    Args:
        user: Django user object
        user_feature_permissions: Dictionary of user permissions
        sections: List of MenuSection objects
        
    Returns:
        list: Filtered list of MenuSection objects
    """
    filtered_sections = []
    
    for section in sections:
        # Check section-level requirements
        if section.requires_superuser and not user.is_superuser:
            continue
        
        if section.requires_staff and not (user.is_staff or user.is_superuser):
            continue
        
        if section.permission:
            if not user_feature_permissions.get(section.permission, False):
                continue
        
        # Filter items in section
        filtered_items = filter_menu_items(user, user_feature_permissions, section.items)
        
        if filtered_items:
            # Create a copy of section with filtered items
            filtered_section = MenuSection(
                name=section.name,
                icon=section.icon,
                items=filtered_items,
                permission=section.permission,
                requires_superuser=section.requires_superuser,
                requires_staff=section.requires_staff
            )
            filtered_sections.append(filtered_section)
    
    return filtered_sections


@register.inclusion_tag('ui/components/menu_item.html', takes_context=True)
def render_menu_item(context, item: MenuItem, menu_type: str = 'mega'):
    """
    Render a single menu item.
    
    Args:
        context: Template context
        item: MenuItem to render
        menu_type: Type of menu ('mega' for top menu, 'sidebar' for sidebar)
        
    Returns:
        dict: Context for menu_item.html template
    """
    user = context.get('user')
    user_feature_permissions = context.get('user_feature_permissions', {})
    
    # Check permission
    if not check_permission(user, user_feature_permissions, item):
        return {'item': None}
    
    # Get URL
    try:
        url = reverse(item.url_name)
    except NoReverseMatch:
        url = '#'
    
    return {
        'item': item,
        'url': url,
        'menu_type': menu_type,
        'has_children': bool(item.children),
    }


@register.inclusion_tag('ui/components/menu_section.html', takes_context=True)
def render_menu_section(context, section: MenuSection, menu_type: str = 'mega'):
    """
    Render a menu section (module).
    
    Args:
        context: Template context
        section: MenuSection to render
        menu_type: Type of menu ('mega' for top menu, 'sidebar' for sidebar)
        
    Returns:
        dict: Context for menu_section.html template
    """
    user = context.get('user')
    user_feature_permissions = context.get('user_feature_permissions', {})
    
    # Filter items
    filtered_items = filter_menu_items(user, user_feature_permissions, section.items)
    
    if not filtered_items:
        return {'section': None}
    
    return {
        'section': section,
        'items': filtered_items,
        'menu_type': menu_type,
    }


@register.simple_tag(takes_context=True)
def get_menu_sections(context):
    """
    Get filtered menu sections for the current user.
    
    Args:
        context: Template context
        
    Returns:
        list: Filtered list of MenuSection objects
    """
    user = context.get('user')
    user_feature_permissions = context.get('user_feature_permissions', {})
    
    if not user or not user.is_authenticated:
        return []
    
    all_sections = get_menu_structure()
    filtered_sections = filter_menu_sections(user, user_feature_permissions, all_sections)
    
    return filtered_sections

