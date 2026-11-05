from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles):
    """
    Decorator to restrict view access to specific user roles.
    allowed_roles: list or tuple of roles (e.g. ['university', 'company', 'ngo', 'administrator'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this area.")
                return redirect('accounts:login')
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to access this resource.")
            return redirect('accounts:dashboard')
        return _wrapped_view
    return decorator


def admin_only(view_func):
    """
    Restrict view to Administrators and superusers.
    """
    return role_required(['administrator'])(view_func)
