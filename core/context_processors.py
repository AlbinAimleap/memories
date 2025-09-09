from accounts.models import Child

def child_context(request):
    """Add child information to template context"""
    if not request.user.is_authenticated:
        return {}
    
    if request.user.is_owner:
        children = Child.objects.filter(owner=request.user)
    else:
        children = request.user.children.all()
    
    return {
        'user_children': children,
        'primary_child': children.first() if children.exists() else None,
    }