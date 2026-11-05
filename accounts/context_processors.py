from .models import UserRole


def user_roles_context(request):
    """
    Expose UserRole choices and helper checks to all templates.
    """
    return {
        'UserRole': UserRole,
        'user_is_org': request.user.is_authenticated and getattr(request.user, 'is_organization', False),
    }
