from rest_framework.permissions import BasePermission


class IsPatientOwner(BasePermission):
    """Object-level permission: only the user who created a patient may access it."""

    message = "You do not have permission to access this patient."

    def has_object_permission(self, request, view, obj):
        return obj.created_by_id == request.user.id
