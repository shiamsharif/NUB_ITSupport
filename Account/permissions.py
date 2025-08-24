from rest_framework.permissions import BasePermission

class IsItStaffOrSuperuser(BasePermission):
    message = "Only IT staff or superusers can create IT staff accounts."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return user.is_superuser or getattr(user, "user_type", None) == "ItStaff"

