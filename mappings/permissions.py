from rest_framework.permissions import BasePermission


class IsMappingPatientOwner(BasePermission):
    """Object-level permission: only the creator of the mapped patient may access it."""

    message = "You do not have permission to access this mapping."

    def has_object_permission(self, request, view, obj):
        return obj.patient.created_by_id == request.user.id
