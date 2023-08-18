def validateRoles(user_roles, required_roles, allowed_roles):
    if "super_admin" in user_roles:
        return True
    has_required_roles = all(role in user_roles for role in required_roles)
    has_allowed_roles = any(role in user_roles for role in allowed_roles)
    if len(required_roles) > 0:
        return has_required_roles
    return has_allowed_roles