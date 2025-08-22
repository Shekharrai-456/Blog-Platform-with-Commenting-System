from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSelfOrAdmin(BasePermission):
    """Users can view/update their own profile; admins can view all."""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            # allow reading your own profile; admins can read all
            return obj == request.user or request.user.is_staff
        # only you or admin can update/delete
        return obj == request.user or request.user.is_staff
