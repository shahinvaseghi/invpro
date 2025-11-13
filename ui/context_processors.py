def active_module(request):
    """
    Returns a simple context dictionary with active module placeholder.
    For now this is static; future iterations can derive from user/company selection.
    """
    return {
        "active_module": request.GET.get("module", "dashboard"),
    }

