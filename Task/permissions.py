from rest_framework import permissions



class IsItStuff(permissions.BasePermission):
    # group_name for super admin
    required_groups = ['admin']

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        # Check if the user is a superuser
        if user.user_type == 'ItStaff':
            return True


