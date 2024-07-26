from application.db.schemas import User
from application.db.dals import PortalRoles


def check_user_permissions(target_user: User, current_user: User) -> bool:
    if target_user.user_id != current_user.user_id:

        if not {
            PortalRoles.ROLE_PORTAL_ADMIN,
            PortalRoles.ROLE_PORTAL_OWNER
        }.intersection(current_user.roles):
            return False

        if (
            PortalRoles.ROLE_PORTAL_OWNER in target_user.roles and
            PortalRoles.ROLE_PORTAL_ADMIN in current_user.roles
        ):
            return False

        if (
            PortalRoles.ROLE_PORTAL_ADMIN in target_user.roles
            and PortalRoles.ROLE_PORTAL_ADMIN in current_user.roles
        ):
            return False

    return True
