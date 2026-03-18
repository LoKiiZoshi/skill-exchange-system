from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsRatedUserReadOnly(permissions.BasePermission):
    """
    Custom permission for rating:
    Allow viewing, but do not allow editing ratings once created.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Do not allow updating or deleting ratings
        return False


class CanRateUser(permissions.BasePermission):
    """
    Permission to check if a user can rate another user.
    Users cannot rate themselves.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            rated_user_id = request.data.get('rated_user')

            if rated_user_id and request.user.is_authenticated:
                if int(rated_user_id) == request.user.id:
                    return False

        return True
