def active_module(request):
    """
    Returns a simple context dictionary with active module placeholder.
    For now this is static; future iterations can derive from user/company selection.
    """
    return {
        "active_module": request.GET.get("module", "dashboard"),
    }


def menu_structure(request):
    """
    Add filtered menu structure to template context.
    
    This provides a centralized menu structure that can be used by both
    top menu and sidebar menu templates.
    """
    from ui.menu_config import get_menu_structure, MenuSection, MenuItem
    
    context = {
        'menu_sections': [],
    }
    
    if not request.user or not request.user.is_authenticated:
        return context
    
    # Get user permissions - try to get from session/active company
    user_feature_permissions = {}
    active_company_id = request.session.get('active_company_id')
    
    if active_company_id:
        from shared.utils.permissions import get_user_feature_permissions
        user_feature_permissions = get_user_feature_permissions(request.user, active_company_id)
    
    # Get all menu sections
    all_sections = get_menu_structure()
    
    # Filter sections based on permissions
    filtered_sections = []
    for section in all_sections:
        # Check section-level requirements
        if section.requires_superuser and not request.user.is_superuser:
            continue
        
        if section.requires_staff and not (request.user.is_staff or request.user.is_superuser):
            continue
        
        if section.permission:
            # استفاده از has_feature_permission برای بررسی صحیح (شامل superuser)
            from shared.utils.permissions import has_feature_permission
            if not has_feature_permission(
                user_feature_permissions,
                section.permission,
                action='view',
                current_user=request.user
            ):
                continue
        
        # Filter items in section
        filtered_items = _filter_menu_items(request.user, user_feature_permissions, section.items)
        
        # اگر section permission نداشته باشد، حتی اگر items خالی باشد، section را نمایش بده
        # (مثل Inventory و Production که در فایل قدیمی همیشه نمایش داده می‌شدند)
        # اما اگر section permission داشته باشد و items خالی باشد، section را نمایش نده
        if filtered_items or not section.permission:
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
    
    context['menu_sections'] = filtered_sections
    return context


def _check_item_permission(user, user_feature_permissions, item) -> bool:
    """Check if user has permission to see a menu item."""
    if item.requires_superuser and not user.is_superuser:
        return False
    
    if item.requires_staff and not (user.is_staff or user.is_superuser):
        return False
    
    # اگر permission داشته باشد، بررسی کن
    if item.permission:
        # استفاده از has_feature_permission برای بررسی صحیح (شامل superuser)
        from shared.utils.permissions import has_feature_permission
        if not has_feature_permission(
            user_feature_permissions,
            item.permission,
            action='view',
            current_user=user
        ):
            return False
    
    return True


def _filter_menu_items(user, user_feature_permissions, items: list) -> list:
    """Filter menu items based on user permissions."""
    from ui.menu_config import MenuItem
    
    filtered_items = []
    
    for item in items:
        if not _check_item_permission(user, user_feature_permissions, item):
            continue
        
        # Recursively filter children
        if item.children:
            filtered_children = _filter_menu_items(user, user_feature_permissions, item.children)
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


