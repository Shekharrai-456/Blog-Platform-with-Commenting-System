from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSelfOrAdmin(BasePermission):
    """
    Allow users to manage their own profile.
    Admins (is_staff) can manage all users.
    """

    def has_permission(self, request, view):
        # Allow safe methods for authenticated users
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # For modifying data, must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admins can do anything
        if request.user and request.user.is_staff:
            return True
        # Users can only access their own object
        return obj == request.user
