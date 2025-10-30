from rest_framework import permissions

class IsOrganizer(permissions.BasePermission):
    """
    Custom permission to only allow organizers of an event to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if obj has organizer attribute (should be Event object)
        if hasattr(obj, 'organizer'):
            return obj.organizer == request.user
        # If obj doesn't have organizer, deny permission
        return False

class IsOrganizerOrPublicReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read access to public events, and full access to organizers.
    For private events, only invited users or organizers can access.
    """

    def has_object_permission(self, request, view, obj):
        # Check if obj has required attributes
        if not hasattr(obj, 'organizer') or not hasattr(obj, 'is_public'):
            return False
            
        # Read permissions are allowed to any request for public events
        if request.method in permissions.SAFE_METHODS:
            if obj.is_public:
                return True
            # For private events, only organizer or invited users
            return obj.organizer == request.user or obj.invitations.filter(user=request.user).exists()
        # Write permissions are only allowed to the organizer
        return obj.organizer == request.user